from django.contrib import admin
from public_modules.models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "job_title", "is_active", "created_on")
    list_filter = ("is_active",)
    search_fields = ("name", "job_title")
