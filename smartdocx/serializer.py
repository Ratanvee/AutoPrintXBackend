from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .models import Note, CustomUser
from django.contrib.auth.models import User
from .models import UploadFiles
# class UserRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password']

#     def create(self, validated_data):
#         user = CustomUser(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import exceptions

class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # The parent method handles token generation (access and refresh)
        return super().get_token(user)

    def validate(self, attrs):
        # 1. Attempt to authenticate with the provided identifier (which could be username or email)
        identifier = attrs.get(self.username_field)
        # print("this is Identifier : ", identifier)
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



from rest_framework import serializers
from .models import CustomUser

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

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'description']


    
# class UploadFilesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadFiles
#         fields = '__all__'


    

# from rest_framework import serializers
# from .models import UploadFiles

# class UploadFilesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadFiles
#         fields = '__all__'
#         read_only_fields = ['Updated_at']


from rest_framework import serializers
from .models import UploadFiles

class UploadFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFiles
        # fields = '__all__'
        fields = ['Unique_url', 'OrderId', 'FileUpload', 'PaperSize', 'PaperType', 'PrintColor', 'PrintSide', 'Binding', 'NumberOfCopies','PaymentAmount', 'PaymentStatus','CustomerName', 'Owner', 'Updated_at', 'Transaction_id', 'NoOfPages', 'PrintStatus', 'Created_at']
        # read_only_fields = ['Updated_at', 'Owner']

    def create(self, validated_data):
        return UploadFiles.objects.create(**validated_data)
