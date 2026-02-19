from django.contrib import admin
from .models.gallery_models import GalleryCategory, GalleryMedia
from .models.content_models import PublicContent


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
  
    list_display = ("name", "created_on")
    search_fields = ("name", "description")
    readonly_fields = ("id", "created_on", "updated_on")
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description")
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )


@admin.register(GalleryMedia)
class GalleryMediaAdmin(admin.ModelAdmin):
 
    list_display = ("title", "category", "uploaded_by", "is_public", "created_on")
    list_filter = ("category", "is_public", "created_on")
    search_fields = ("title", "description")
    readonly_fields = ("id", "created_on", "updated_on")
    fieldsets = (
        ("Media Information", {
            "fields": ("category", "title", "description")
        }),
        ("File & Metadata", {
            "fields": ("media_url", "uploaded_by", "is_public")
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )


@admin.register(PublicContent)
class PublicContentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "subtitle", "value", "order", "is_active", "created_on")
    list_filter = ("category", "is_active", "created_on")
    search_fields = ("title", "subtitle", "text_content", "email", "phone", "first_name", "last_name")
    ordering = ("category", "order", "-created_on")
    readonly_fields = ("id", "created_on", "updated_on", "fullname")
    
    fieldsets = (
        ("Classification", {
            "fields": ("category", "order", "is_active")
        }),
        ("Content (Impact / Team / Story / Info)", {
            "fields": ("title", "subtitle", "value", "text_content", "image")
        }),
        ("Contact Message Data (If applicable)", {
            "fields": ("first_name", "last_name", "email", "phone", "admin_notes", "fullname"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )
