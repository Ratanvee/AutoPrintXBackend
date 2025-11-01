from django.contrib import admin
from .models import UploadFiles, CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import OTPVerification

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UploadFiles)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['email_or_phone', 'otp', 'is_verified', 'created_at', 'attempts', 'expires_at', 'max_attempts', 'purpose']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email_or_phone', 'otp']
    readonly_fields = ['created_at', 'expires_at']
