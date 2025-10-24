from django.contrib import admin
from .models import UploadFiles, CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(CustomUser)
# admin.site.register(Note)
admin.site.register(UploadFiles)
# This will allow you to manage Note objects from the Django admin interface.