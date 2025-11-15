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


# class UploadFiles(models.Model):
#     Unique_url = models.CharField(max_length=255, blank=True, null=True)
#     OrderId = models.CharField(max_length=100, blank=True, null=True)
#     FileUpload = models.TextField(default='', blank=True, null=True)  
#     FileUploadID = models.CharField(max_length=255, default='', blank=True, null=True) 
#     PaperSize = models.CharField(max_length=20, default='A4')
#     PaperType = models.CharField(max_length=20, default='Portrait')
#     PrintColor = models.CharField(max_length=20, default='Color')
#     PrintSide = models.CharField(max_length=20, default='One-sided')
#     Binding = models.CharField(max_length=20, default='None')
#     NumberOfCopies = models.IntegerField(default=1)
#     PaymentStatus = models.BooleanField(default=False)
#     PaymentAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     PaymentMethod = models.CharField(max_length=50, default='Cash')
#     Owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploads')
#     Updated_at = models.DateTimeField(auto_now=True)
#     Transaction_id = models.CharField(max_length=100, blank=True, null=True)
#     NoOfPages = models.IntegerField(default=0)
#     CustomerName = models.CharField(max_length=100, blank=True, null=True)
#     PrintStatus = models.CharField(max_length=50, default='Pending')  # e.g., Pending, In Progress, Completed
#     Created_at = models.DateTimeField(default=timezone.now)  # Tracks order creation

#     def __str__(self):
#         return f"Order {self.id} - {self.Owner}"

#     class Meta:
#         verbose_name_plural = "Uploaded Files"


# Step 1: Keep your model as BooleanField (Djongo compatible)
# models.py
from django.db import models
from django.utils import timezone
import json

class UploadFiles(models.Model):
    Unique_url = models.CharField(max_length=255, blank=True, null=True)
    OrderId = models.CharField(max_length=100, blank=True, null=True)
    
    # Store multiple file URLs as JSON
    FileUpload = models.TextField(default='{}', blank=True, null=True, 
                                   help_text="JSON dictionary of filename: file_url")
    
    # Store multiple file IDs as JSON
    FileUploadID = models.TextField(default='{}', blank=True, null=True,
                                     help_text="JSON dictionary of filename: file_id")
    
    # ✅ NEW: Store page counts for each file as JSON
    FilePagesCount = models.TextField(default='{}', blank=True, null=True,
                                       help_text="JSON dictionary of filename: page_count")
    
    PaperSize = models.CharField(max_length=20, default='A4')
    PaperType = models.CharField(max_length=20, default='Portrait')
    PrintColor = models.CharField(max_length=20, default='Color')
    PrintSide = models.CharField(max_length=20, default='One-sided')
    Binding = models.CharField(max_length=20, default='None')
    NumberOfCopies = models.IntegerField(default=1)
    PaymentStatus = models.BooleanField(default=False)
    PaymentAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    PaymentMethod = models.CharField(max_length=50, default='Cash')
    Owner = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='uploads')
    Updated_at = models.DateTimeField(auto_now=True)
    Transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # ✅ UPDATED: Now stores total pages across all files
    NoOfPages = models.IntegerField(default=0, help_text="Total pages across all files")
    
    CustomerName = models.CharField(max_length=100, blank=True, null=True)
    PrintStatus = models.CharField(max_length=50, default='Pending')
    Created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} - {self.Owner}"

    class Meta:
        verbose_name_plural = "Uploaded Files"
        ordering = ['-Created_at']
    
    # Helper methods for multi-file support
    def get_file_urls(self):
        """Return dictionary of file URLs from JSON string"""
        if not self.FileUpload:
            return {}
        
        try:
            data = json.loads(self.FileUpload)
            if isinstance(data, dict):
                return data
            elif isinstance(data, str):
                return {"file": data}
            return {}
        except (json.JSONDecodeError, TypeError):
            if self.FileUpload.startswith(('http://', 'https://')):
                return {"file": self.FileUpload}
            return {}
    
    def get_file_ids(self):
        """Return dictionary of file IDs from JSON string"""
        if not self.FileUploadID:
            return {}
        
        try:
            data = json.loads(self.FileUploadID)
            if isinstance(data, dict):
                return data
            elif isinstance(data, str):
                return {"file": data}
            return {}
        except (json.JSONDecodeError, TypeError):
            if self.FileUploadID:
                return {"file": self.FileUploadID}
            return {}
    
    # ✅ NEW: Helper method for page counts
    def get_file_pages(self):
        """Return dictionary of page counts from JSON string"""
        if not self.FilePagesCount:
            return {}
        
        try:
            data = json.loads(self.FilePagesCount)
            if isinstance(data, dict):
                return data
            elif isinstance(data, (int, str)):
                # Single file backward compatibility
                return {"file": int(data)}
            return {}
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}
    
    def get_file_count(self):
        """Return number of files in this order"""
        return len(self.get_file_urls())
    
    def get_total_pages(self):
        """Return total pages across all files"""
        page_counts = self.get_file_pages()
        return sum(page_counts.values()) if page_counts else self.NoOfPages
    
    def get_first_file_url(self):
        """Get the first file URL (for backward compatibility)"""
        urls = self.get_file_urls()
        if urls:
            return list(urls.values())[0]
        return None
    
    def set_file_urls(self, file_dict):
        """Set file URLs from dictionary"""
        self.FileUpload = json.dumps(file_dict)
    
    def set_file_ids(self, file_dict):
        """Set file IDs from dictionary"""
        self.FileUploadID = json.dumps(file_dict)
    
    # ✅ NEW: Setter for page counts
    def set_file_pages(self, pages_dict):
        """Set page counts from dictionary"""
        self.FilePagesCount = json.dumps(pages_dict)
        # Also update NoOfPages with total
        self.NoOfPages = sum(pages_dict.values()) if pages_dict else 0

        
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
        
class WebLoginToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)   
