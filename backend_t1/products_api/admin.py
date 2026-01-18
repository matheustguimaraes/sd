from django.contrib import admin
from django.utils.html import format_html
from products_api.models import Product, Profile
from products_api.utils import get_s3_url


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "age", "course", "city", "created_at"]
    list_filter = ["created_at", "city", "course"]
    search_fields = ["user__username", "user__email", "course", "city"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "image_preview", "name", "user", "price", "created_at"]
    list_filter = ["created_at", "user"]
    search_fields = ["name", "description", "user__username"]
    readonly_fields = ["image_preview_detail", "thumbnail_preview", "created_at", "updated_at"]

    def image_preview(self, obj):
        """Show thumbnail image in list view."""
        if obj.image_thumbnail_s3_key:
            url = get_s3_url(obj.image_thumbnail_s3_key)
            if url:
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                    url,
                )
        elif obj.image_s3_key:
            url = get_s3_url(obj.image_s3_key)
            if url:
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                    url,
                )
        return format_html('<span style="color: #999;">Sem imagem</span>')

    image_preview.short_description = "Imagem"

    def image_preview_detail(self, obj):
        """Show full image in detail view."""
        if obj.image_s3_key:
            url = get_s3_url(obj.image_s3_key)
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
                    url,
                )
        return format_html('<span style="color: #999;">Sem imagem</span>')

    image_preview_detail.short_description = "Imagem Original"

    def thumbnail_preview(self, obj):
        """Show thumbnail in detail view."""
        if obj.image_thumbnail_s3_key:
            url = get_s3_url(obj.image_thumbnail_s3_key)
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
                    url,
                )
        return format_html('<span style="color: #999;">Sem thumbnail</span>')

    thumbnail_preview.short_description = "Thumbnail"

    fieldsets = (
        (
            "Informações Básicas",
            {
                "fields": ("user", "name", "description", "price"),
            },
        ),
        (
            "Imagens",
            {
                "fields": ("image_preview_detail", "thumbnail_preview", "image_s3_key", "image_thumbnail_s3_key"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
