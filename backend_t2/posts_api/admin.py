from django.contrib import admin
# from django.utils.html import format_html
from posts_api.models import Posts, Profile, Upload, UploadPrivate
# from posts_api.utils import get_s3_url


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "age", "course", "city", "created_at"]
    list_filter = ["created_at", "city", "course"]
    search_fields = ["user__username", "user__email", "course", "city"]
    readonly_fields = ["created_at", "updated_at"]


# @admin.register(Posts)
# class PostsAdmin(admin.ModelAdmin):
#     list_display = ["id", "user", "name", "image_preview", "price", "description", "created_at", "updated_at"]
#     list_filter = ["created_at", "user"]
#     search_fields = ["user__username", "name", "description"]
#     readonly_fields = ["image_preview_detail", "thumbnail_preview", "image_s3_key", "image_thumbnail_s3_key", "created_at", "updated_at"]

#     def image_preview(self, obj):
#         """Show thumbnail image in list view."""
#         try:
#             if obj.image_thumbnail_s3_key:
#                 url = get_s3_url(obj.image_thumbnail_s3_key)
#                 if url:
#                     return format_html(
#                         '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
#                         url,
#                     )
#             elif obj.image_s3_key:
#                 url = get_s3_url(obj.image_s3_key)
#                 if url:
#                     return format_html(
#                         '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
#                         url,
#                     )
#         except Exception:
#             pass
#         return format_html('<span style="color: #999;">Sem imagem</span>')

#     image_preview.short_description = "Imagem"

#     def image_preview_detail(self, obj):
#         """Show full image in detail view."""
#         try:
#             if obj.image_s3_key:
#                 url = get_s3_url(obj.image_s3_key)
#                 if url:
#                     return format_html(
#                         '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
#                         url,
#                     )
#         except Exception:
#             pass
#         return format_html('<span style="color: #999;">Sem imagem</span>')

#     image_preview_detail.short_description = "Imagem Original"

#     def thumbnail_preview(self, obj):
#         """Show thumbnail in detail view."""
#         try:
#             if obj.image_thumbnail_s3_key:
#                 url = get_s3_url(obj.image_thumbnail_s3_key)
#                 if url:
#                     return format_html(
#                         '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
#                         url,
#                     )
#         except Exception:
#             pass
#         return format_html('<span style="color: #999;">Sem thumbnail</span>')

#     thumbnail_preview.short_description = "Thumbnail"

#     fieldsets = (
#         (
#             "Informações Básicas",
#             {
#                 "fields": ("user", "name", "description", "price"),
#             },
#         ),
#         (
#             "Imagens",
#             {
#                 "fields": ("image_preview_detail", "thumbnail_preview", "image_s3_key", "image_thumbnail_s3_key"),
#             },
#         ),
#         (
#             "Metadata",
#             {
#                 "fields": ("created_at", "updated_at"),
#                 "classes": ("collapse",),
#             },
#         ),
#     )
admin.site.register(Posts)
admin.site.register(Upload)
admin.site.register(UploadPrivate)
