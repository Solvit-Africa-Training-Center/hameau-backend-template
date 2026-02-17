from django.contrib import admin
from .models.gallery_models import GalleryCategory, GalleryMedia
from .models.impact_models import ImpactStatistic, ContactMessage, ContactInfo
from .models.team_models import TeamMember


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


@admin.register(ImpactStatistic)
class ImpactStatisticAdmin(admin.ModelAdmin):
 
    list_display = ("title", "value", "order", "is_active", "created_on")
    list_filter = ("is_active", "created_on")
    search_fields = ("title", "description")
    ordering = ("order",)
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "value", "description")
        }),
        ("Display Settings", {
            "fields": ("order", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_on", "updated_on")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    
    list_display = ("get_fullname", "email", "subject", "status", "created_on")
    list_filter = ("status", "created_on")
    search_fields = ("first_name", "last_name", "email", "subject", "message")
    readonly_fields = ("id", "created_on", "updated_on")
    fieldsets = (
        ("Sender Information", {
            "fields": ("first_name", "last_name", "email", "phone")
        }),
        ("Message", {
            "fields": ("subject", "message")
        }),
        ("Admin Status", {
            "fields": ("status", "admin_notes")
        }),
        ("Timestamps", {
            "fields": ("id", "created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )
    actions = ["mark_as_viewed", "mark_as_responded"]

    def get_fullname(self, obj):
      
        return obj.fullname
    get_fullname.short_description = "Sender Name"

    def mark_as_viewed(self, request, queryset):
        
        updated = queryset.update(status=ContactMessage.VIEWED)
        self.message_user(request, f"{updated} message(s) marked as viewed.")
    mark_as_viewed.short_description = "Mark selected as viewed"

    def mark_as_responded(self, request, queryset):
        
        updated = queryset.update(status=ContactMessage.RESPONDED)
        self.message_user(request, f"{updated} message(s) marked as responded.")
    mark_as_responded.short_description = "Mark selected as responded"


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    
    list_display = ("email", "phone", "is_active", "created_on")
    list_filter = ("is_active", "created_on")
    search_fields = ("email", "phone", "address")
    readonly_fields = ("created_on", "updated_on")
    fieldsets = (
        ("Contact Details", {
            "fields": ("email", "phone", "address")
        }),
        ("Business Hours", {
            "fields": ("office_hours",)
        }),
        ("Display", {
            "fields": ("is_active",)
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
   
    list_display = ("first_name", "last_name", "role", "is_active", "created_on")
    list_filter = ("is_active", "created_on")
    search_fields = ("first_name", "last_name", "role")
    readonly_fields = ("created_on", "updated_on")
    fieldsets = (
        ("Basic Information", {
            "fields": ("first_name", "last_name", "role")
        }),
        ("Photo", {
            "fields": ("photo",)
        }),
        ("Display", {
            "fields": ("order", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",)
        }),
    )

