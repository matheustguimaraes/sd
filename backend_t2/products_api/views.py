from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from products_api.models import Product, Profile
from products_api.serializers import ProductSerializer, ProfileSerializer
from products_api.utils import (
    upload_to_s3,
    log_crud_action,
    get_s3_url,
    publish_to_rabbitmq,
)

import uuid
from datetime import datetime


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "name"]

    def perform_create(self, serializer):
        product = serializer.save(user=self.request.user)
        log_crud_action(
            action_type="CREATE",
            model_name="Product",
            data={"id": product.id, "name": product.name, "price": str(product.price)},
            user_id=self.request.user.id,
        )

    def perform_update(self, serializer):
        product = serializer.save()
        log_crud_action(
            action_type="UPDATE",
            model_name="Product",
            data={"id": product.id, "name": product.name, "price": str(product.price)},
            user_id=self.request.user.id,
        )

    def perform_destroy(self, instance):
        product_id = instance.id
        product_name = instance.name
        instance.delete()
        log_crud_action(
            action_type="DELETE",
            model_name="Product",
            data={"id": product_id, "name": product_name},
            user_id=self.request.user.id,
        )

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        log_crud_action(
            action_type="READ",
            model_name="Product",
            data={"action": "list"},
            user_id=request.user.id,
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        log_crud_action(
            action_type="READ",
            model_name="Product",
            data={"id": kwargs.get("pk")},
            user_id=request.user.id,
        )
        return response

    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        product: Product = self.get_object()

        if "image" not in request.FILES:
            return Response(
                {"error": "Nenhuma imagem fornecida"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES["image"]

        s3_key = f"products/{product.id}/{uuid.uuid4()}_{image_file.name}"

        try:
            upload_to_s3(image_file, s3_key)
            product.image_s3_key = s3_key
            product.save()

            message = {
                "action": "process_image",
                "product_id": product.id,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat(),
            }
            publish_to_rabbitmq(message)

            log_crud_action(
                action_type="UPDATE",
                model_name="Product",
                data={"id": product.id, "action": "image_upload", "s3_key": s3_key},
                user_id=request.user.id,
            )

            return Response(
                {
                    "message": "Imagem enviada com sucesso",
                    "s3_key": s3_key,
                    "image_url": get_s3_url(s3_key),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao fazer upload: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_crud_action(
                action_type="UPDATE",
                model_name="Profile",
                data={
                    "id": profile.id,
                    "age": serializer.validated_data.get("age"),
                    "course": serializer.validated_data.get("course"),
                    "city": serializer.validated_data.get("city"),
                },
                user_id=request.user.id,
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    from django.contrib.auth import get_user_model

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "Todos os campos são obrigatórios"}, status=400)

    User = get_user_model()

    if User.objects.filter(username=username).exists():
        return Response({"error": "Usuário já existe"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email já está em uso"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    Profile.objects.create(user=user)
    return Response({"message": "Usuário criado com sucesso"}, status=201)
