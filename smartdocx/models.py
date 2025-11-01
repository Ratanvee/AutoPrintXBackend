from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random

class CustomUser(AbstractUser):
    unique_url = models.CharField(max_length=255, unique=True, blank=True, null=True)
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    owner_fullname = models.CharField(max_length=255, blank=True, null=True, default="")
    owner_phone_number = models.CharField(max_length=15, blank=True, null=True)
    owner_shop_address = models.CharField(max_length=255, blank=True, null=True)
    info_modified = models.BooleanField(default=False)
    owner_nationality = models.CharField(max_length=10, default="IN")
    owner_shop_image = models.CharField(max_length=100, blank=True, null=True)
    id = models.AutoField(primary_key=True)  # Ensure it's an integer, not an ObjectId

    # Fix conflicting reverse accessors
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",  # Unique related name to prevent conflicts
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",  # Unique related name to prevent conflicts
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.unique_url:  # Generate only if empty
            base_url = self.username.lower().replace(" ", "-")
            unique_part = str(uuid.uuid4())
            self.unique_url = f"{base_url}-{unique_part}"

            # Ensure uniqueness in the database
            while CustomUser.objects.filter(unique_url=self.unique_url).exists():
                unique_part = str(uuid.uuid4())
                self.unique_url = f"{base_url}-{unique_part}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class UploadFiles(models.Model):
    Unique_url = models.CharField(max_length=255, blank=True, null=True)
    OrderId = models.CharField(max_length=100, blank=True, null=True)
    FileUpload = models.TextField(default='', blank=True, null=True)  
    FileUploadID = models.CharField(max_length=255, default='', blank=True, null=True) 
    PaperSize = models.CharField(max_length=20, default='A4')
    PaperType = models.CharField(max_length=20, default='Portrait')
    PrintColor = models.CharField(max_length=20, default='Color')
    PrintSide = models.CharField(max_length=20, default='One-sided')
    Binding = models.CharField(max_length=20, default='None')
    NumberOfCopies = models.IntegerField(default=1)
    PaymentStatus = models.BooleanField(default=False)
    PaymentAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    PaymentMethod = models.CharField(max_length=50, default='Cash')
    Owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploads')
    Updated_at = models.DateTimeField(auto_now=True)
    Transaction_id = models.CharField(max_length=100, blank=True, null=True)
    NoOfPages = models.IntegerField(default=0)
    CustomerName = models.CharField(max_length=100, blank=True, null=True)
    PrintStatus = models.CharField(max_length=50, default='Pending')  # e.g., Pending, In Progress, Completed
    Created_at = models.DateTimeField(default=timezone.now)  # Tracks order creation

    def __str__(self):
        return f"Order {self.id} - {self.Owner}"

    class Meta:
        verbose_name_plural = "Uploaded Files"


class OTPVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email_or_phone = models.CharField(max_length=255)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    purpose = models.CharField(max_length=50, default='forgot_password', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Set expiry time to 10 minutes from creation"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def can_attempt(self):
        """Allow max attempts"""
        return self.attempts < self.max_attempts
    
    @staticmethod
    def generate_otp():
        """Generate 4-digit OTP"""
        return str(random.randint(1000, 9999))
    
    @staticmethod
    def delete_expired():
        """Delete all expired OTP records one by one"""
        try:
            expired_otps = OTPVerification.objects.filter(expires_at__lt=timezone.now())
            count = 0
            for otp in expired_otps:
                otp.delete()
                count += 1
            return count
        except Exception as e:
            print(f"Error deleting expired OTPs: {e}")
            return 0