from django.contrib import admin
from .models import UploadFiles, CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(CustomUser)
# admin.site.register(Note)
admin.site.register(UploadFiles)
# This will allow you to manage Note objects from the Django admin interface.

# admin.py (Optional - for managing OTPs in admin panel)
from django.contrib import admin
from .models import OTPVerification

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['email_or_phone', 'otp', 'is_verified', 'created_at', 'attempts', 'expires_at', 'max_attempts', 'purpose']
    # list_filter = ['is_verified', 'created_at']
    # search_fields = ['email_or_phone', 'otp']
    # readonly_fields = ['created_at', 'expires_at']
