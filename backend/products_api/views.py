import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from products_api.environment_variables import USE_S3, SERVICE_API_TOKEN
from products_api.models import Product, Profile
from products_api.serializers import ProductSerializer, ProfileSerializer
from products_api.utils import (
    log_crud_action,
    publish_to_sns,
)

from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from products_api.models import UploadPrivate


def image_upload(request):
    if request.method == "POST":
        image_file = request.FILES["image_file"]
        # Verifica se S3 está configurado corretamente (bucket name não vazio)
        if USE_S3:
            upload = UploadPrivate(file=image_file)
            upload.save()
            image_url = upload.file.url
        else:
            # Usa armazenamento local se S3 não estiver configurado
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
        return render(request, "upload.html", {"image_url": image_url})
    return render(request, "upload.html")


@method_decorator(csrf_exempt, name="dispatch")
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

        if "image" not in request.FILES:  # pyright: ignore[reportUnreachable]
            return Response(
                {"error": "Nenhuma imagem fornecida"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES["image"]

        try:
            # Usa UploadPrivate para armazenar imagens de forma privada
            upload = UploadPrivate(file=image_file)
            upload.save()

            # Salva a chave S3 no produto (o file.name já inclui o location prefix se usar S3)
            product.image_s3_key = upload.file.name
            product.save()

            message = {
                "action": "process_image",
                "product_id": product.id,
                "s3_key": upload.file.name,
                "timestamp": datetime.now().isoformat(),
            }
            publish_to_sns(message)

            log_crud_action(
                action_type="UPDATE",
                model_name="Product",
                data={"id": product.id, "action": "image_upload", "s3_key": upload.file.name},
                user_id=request.user.id,
            )

            return Response(
                {
                    "message": "Imagem enviada com sucesso",
                    "s3_key": upload.file.name,
                    "image_url": upload.file.url,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Erro ao fazer upload: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": f"Erro ao fazer upload: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], permission_classes=[AllowAny], url_path="register-bw-image")
    def register_bw_image(self, request, pk=None):
        """Registra no banco a chave P&B enviada pela Lambda."""
        service_token = request.headers.get("X-Service-Token", "")
        if not SERVICE_API_TOKEN or service_token != SERVICE_API_TOKEN:
            return Response(
                {"error": "Acesso não autorizado"},
                status=status.HTTP_403_FORBIDDEN,
            )

        image_bw_s3_key = request.data.get("image_bw_s3_key")
        if not image_bw_s3_key:
            return Response(
                {"error": "Campo image_bw_s3_key é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product: Product = self.get_object()
        product.image_bw_s3_key = image_bw_s3_key
        product.save(update_fields=["image_bw_s3_key"])

        log_crud_action(
            action_type="UPDATE",
            model_name="Product",
            data={"id": product.id, "action": "image_bw_registered", "s3_key": image_bw_s3_key},
            user_id=self.request.user.id if self.request.user.is_authenticated else None,
        )

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get or update user profile."""
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


@api_view(["POST", "OPTIONS"])
@authentication_classes([])  # No authentication required for registration
@permission_classes([AllowAny])
def register_view(request):
    # Handle CORS preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response(status=200)

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
    # Create profile automatically when user registers
    Profile.objects.create(user=user)
    return Response({"message": "Usuário criado com sucesso"}, status=201)
