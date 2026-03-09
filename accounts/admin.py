from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User
from django.utils.crypto import get_random_string
# Register your models here.


admin.site.site_header = "Hameau Des Jeune Admin Portal"
admin.site.site_title = "Hameau Des Jeune"
admin.site.index_title = "Welcome to the Admin Dashboard"

