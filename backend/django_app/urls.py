from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from products_api.views import ProductViewSet, register_view, profile_view, image_upload

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")

schema_view = get_schema_view(
    openapi.Info(
        title="MDCC SD Image Processing API",
        default_version="v1",
        description="API para processamento de imagens com AWS S3",
        terms_of_service="https://mdcc.sd.br",
        contact=openapi.Contact(email="mdcc.sd@gmail.com"),
    ),
    public=True,
)

urlpatterns = [
    path("api/", include([
        path("", include(router.urls)),
        path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("auth/register/", register_view, name="register"),
        path("auth/profile/", profile_view, name="profile"),
        path("upload/", image_upload, name="image_upload"),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path("admin/", admin.site.urls),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
