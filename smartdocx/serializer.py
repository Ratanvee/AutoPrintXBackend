from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .models import CustomUser, UploadFiles
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from .models import OTPVerification


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # The parent method handles token generation (access and refresh)
        return super().get_token(user)

    def validate(self, attrs):
        # 1. Attempt to authenticate with the provided identifier (which could be username or email)
        identifier = attrs.get(self.username_field)
        password = attrs.get('password')
        
        # Start with the default authentication attempt (e.g., username)
        user = authenticate(
            request=self.context.get('request'),
            username=identifier,
            password=password
        )

        # 2. If the first attempt failed, try to authenticate by email
        if user is None:
            try:
                # Assuming your User model has an 'email' field
                # Look up the user by email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                user = User.objects.get(email__iexact=identifier)
                
                # Check the password manually since 'authenticate' failed
                if not user.check_password(password):
                     # If password check fails, set user back to None to trigger the final error
                    user = None 
                
            except User.DoesNotExist:
                # If lookup by email also fails, the user is still None
                pass
        
        # 3. Final Check and Token Generation
        if user is None or not user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        
        # Set the authenticated user on the serializer instance
        self.user = user

        # Manually generate tokens after successful authentication
        refresh = self.get_token(user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=4)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']


# class UploadFilesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadFiles
#         # fields = '__all__'
#         fields = ['Unique_url', 'OrderId', 'FileUpload', 'FileUploadID', 'PaperSize', 'PaperType', 'PrintColor', 'PrintSide', 'Binding', 'NumberOfCopies', 'PaymentAmount', 'PaymentStatus', 'CustomerName', 'Owner', 'Updated_at', 'Transaction_id', 'NoOfPages', 'PrintStatus', 'Created_at']
#         # read_only_fields = ['Updated_at', 'Owner']

#     def create(self, validated_data):
#         return UploadFiles.objects.create(**validated_data)

from rest_framework import serializers
from smartdocx.models import UploadFiles
import json

class UploadFilesSerializer(serializers.ModelSerializer):
    file_urls = serializers.SerializerMethodField()
    file_ids = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadFiles
        fields = [
            'id',
            'Owner',
            'Unique_url',
            'FileUpload',
            'FileUploadID',
            'file_urls',
            'file_ids',
            'file_count',
            'PaperSize',
            'PaperType',
            'PrintColor',
            'PrintSide',
            'Binding',
            'NumberOfCopies',
            'PaymentAmount',
            'NoOfPages',
            'PaymentStatus',  # BooleanField
            'Transaction_id',
            'CustomerName',
            'OrderId',
            'PaymentMethod',
            'PrintStatus',
            'Created_at',
            'Updated_at',
            'FilePagesCount'
        ]
        read_only_fields = ['id', 'Created_at', 'Updated_at']
    
    def get_file_urls(self, obj):
        """Return parsed file URLs dictionary"""
        return obj.get_file_urls()
    
    def get_file_ids(self, obj):
        """Return parsed file IDs dictionary"""
        return obj.get_file_ids()
    
    def get_file_count(self, obj):
        """Return number of files"""
        return obj.get_file_count()
    
    def validate_FileUpload(self, value):
        """Validate that FileUpload is valid JSON or string"""
        if not value:
            return '{}'
        
        if isinstance(value, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(value)
                # Ensure it's stored as JSON string
                return json.dumps(parsed)
            except json.JSONDecodeError:
                # If not JSON, check if it's a URL (backward compatibility)
                if value.startswith(('http://', 'https://')):
                    # Wrap single URL in dict format
                    return json.dumps({"file": value})
                raise serializers.ValidationError("Invalid file URL format")
        
        # If it's already a dict, convert to JSON
        if isinstance(value, dict):
            return json.dumps(value)
        
        return value
    
    def validate_FileUploadID(self, value):
        """Validate that FileUploadID is valid JSON or string"""
        if not value:
            return '{}'
        
        if isinstance(value, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(value)
                return json.dumps(parsed)
            except json.JSONDecodeError:
                # If not JSON, wrap in dict (backward compatibility)
                if value:
                    return json.dumps({"file": value})
                return '{}'
        
        # If it's already a dict, convert to JSON
        if isinstance(value, dict):
            return json.dumps(value)
        
        return value
    
    def validate_PaymentStatus(self, value):
        """Ensure PaymentStatus is boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        if isinstance(value, int):
            return bool(value)
        return False

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    Expects 'old_password', 'new_password', and 'confirm_password'.
    """
    newPassword = serializers.CharField(required=True)
    confirmPassword = serializers.CharField(required=True)
    currentPassword = serializers.CharField(required=True)

    def validate(self, data):
        """
        Runs validation checks:
        1. New password matches confirmation.
        2. Old password is correct for the current user.
        3. New password is not the same as the old password.
        """
        # print("This is data in serializer validate: ", data)
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')
        old_password = data.get('currentPassword')

        # Check 1: New password and confirmation must match
        if new_password != confirm_password:
            raise serializers.ValidationError({
                "error": "New password and confirmation do not match."
            })

        # Get the user object from the serializer context (passed from the view)
        user = self.context.get('request').user

        # Check 2: Old password must be correct
        # check_password() is a Django function that correctly hashes and compares passwords.
        if not user.check_password(old_password):
            raise serializers.ValidationError({
                "error": "The old password entered is incorrect."
            })

        # Check 3: New password cannot be the same as the old password (security best practice)
        if old_password == new_password:
             raise serializers.ValidationError({
                "error": "The new password cannot be the same as the old password."
             })

        return data


User = get_user_model()
class SendOTPSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255)
    purpose = serializers.ChoiceField(
        choices=['signup', 'forgot_password'],
        default='forgot_password',
        required=False
    )
    
    def validate_email_or_phone(self, value):
        """Basic validation - check if it's a valid email format"""
        if '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address.")
        return value
    
    def validate(self, data):
        """
        Cross-field validation based on purpose
        This runs after individual field validation
        """
        email_or_phone = data.get('email_or_phone')
        purpose = data.get('purpose', 'forgot_password')
        
        # Check if it's an email
        if '@' in email_or_phone:
            user_exists = User.objects.filter(email=email_or_phone).exists()
            
            if purpose == 'forgot_password':
                # For forgot password, user MUST exist
                if not user_exists:
                    raise serializers.ValidationError({
                        "email_or_phone": "No account found with this email."
                    })
            
            elif purpose == 'signup':
                # For signup, user MUST NOT exist
                if user_exists:
                    raise serializers.ValidationError({
                        "email_or_phone": "An account with this email already exists."
                    })
        
        return data


class VerifyOTPSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255)
    otp = serializers.CharField(max_length=4)
    
    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("OTP must be 4 digits.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255)
    new_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate_email_or_phone(self, value):
        """Validate email or phone format"""
        if not value:
            raise serializers.ValidationError("Email or phone number is required.")
        return value
    
    def validate_new_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Optional: Add more password strength validations if needed
        # if not any(char.isdigit() for char in value):
        #     raise serializers.ValidationError("Password must contain at least one number.")
        
        # if not any(char.isupper() for char in value):
        #     raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        return value