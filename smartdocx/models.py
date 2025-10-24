from django.db import models
# from django.contrib.auth.models import User
# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    unique_url = models.CharField(max_length=255, unique=True, blank=True, null=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_customers = models.IntegerField(default=0)
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




# class Note(models.Model):
#     owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notes')
#     description = models.TextField(max_length=300)

# # class UploadFiles(models.Model):
# #     FileUpload = models.FileField(upload_to='uploads/', blank=True, null=True)
# #     PaperSize = models.CharField(max_length=20, default='A4')
# #     PaperType = models.CharField(max_length=20, default='Portrait')
# #     PrintColor = models.CharField(max_length=20, default='Color')
# #     PrintSide = models.CharField(max_length=20, default='One-sided')
# #     Binding = models.CharField(max_length=20, default='None')
# #     NumberOfCopies = models.IntegerField(default=1)
# #     PaymentStatus = models.BooleanField(default=False)
# #     Owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
# #     Updated_at = models.DateTimeField(auto_now=True)
# #     Transaction_id = models.CharField(max_length=100, blank=True, null=True)
# #     NoOfPages = models.IntegerField(default=0)

# #     def __str__(self):
# #         return f"Order {self.id} - {self.Owner}"


# # models.py
import uuid
# # from django.contrib.auth.models import User

# class Profile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
#     unique_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

#     def __str__(self):
#         return f"{self.user.username} - {self.unique_id}"


# def upload_to_path():
#     return f'upload/'

from django.utils import timezone
class UploadFiles(models.Model):
    Unique_url = models.CharField(max_length=255, blank=True, null=True)
    OrderId = models.CharField(max_length=100, blank=True, null=True)
    # FileUpload = models.FileField(upload_to='documents/', blank=True, null=True)
    FileUpload = models.CharField(max_length=100, blank=True, null=True)
    # FileUrl = models.CharField(max_length=500, blank=True, null=True) # ADD THIS
    # FileId = models.CharField(max_length=255, blank=True, null=True)  # Store ImageKit's File ID
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




# # Payment gateway models
# class PaymentGateway(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     api_key = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name