# from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.shortcuts import render, HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import time
from rest_framework.permissions import IsAuthenticated, AllowAny

# from .models import Note, CustomUser, UploadFiles, Profile
from .serializer import  UserRegisterSerializer, UserSerializer
# from .models import UploadFiles
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Initialise environment variables
import environ
env = environ.Env()
environ.Env.read_env()

# For API testing
# @api_view(['GET'])
# def home(request):
#     time.sleep(1)
#     return Response({
#         'name': 'Ratan',
#         'email': 'ratan@example.com',
#         'role': 'Developer'
#     })

# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         try:
#             response = super().post(request, *args, **kwargs)
#             tokens = response.data
#             # access_token = tokens.get('access')
#             access_token = tokens['access']
#             # refresh_token = tokens.get('refresh')
#             refresh_token = tokens['refresh']
#             print(f"Access Token: {access_token}")
#             print(f"Refresh Token: {refresh_token}")

#             res = Response()

#             res.data = {'success': True, 'AccessToken': access_token, 'RefreshToken': refresh_token}


#             # Cookie valid for 7 days (in seconds)
#             cookie_age = 7 * 24 * 60 * 60

#             res.set_cookie(
#                 key = 'access_token',
#                 value = access_token,
#                 httponly = True,
#                 secure = True,
#                 samesite = 'None',
#                 path = '/',
#                 max_age=cookie_age,  # ← cookie expiry time
#             )

#             res.set_cookie(
#                 key = 'refresh_token',
#                 value = refresh_token,
#                 httponly = True,
#                 secure = True,
#                 samesite = 'None',
#                 path = '/',
#                 max_age=cookie_age * 4,  # refresh token can last longer (e.g., 28 days)
#             )
#             return res
#         # except:
#         #     return Response({'success': False})
#         except Exception as e:
#             # Catch any other unexpected exceptions
#             return Response(f"An unexpected error occurred: {e}")


# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework.response import Response
# # Import your custom serializer
# from .serializer import EmailOrUsernameTokenObtainPairSerializer 
# # (assuming you placed the serializer in a 'serializers.py' file)

# class CustomTokenObtainPairView(TokenObtainPairView):
#     # ⭐ Set the custom serializer class
#     serializer_class = EmailOrUsernameTokenObtainPairSerializer 

#     def post(self, request, *args, **kwargs):
#         try:
#             # Calls the custom serializer's validate method
#             response = super().post(request, *args, **kwargs)
            
#             tokens = response.data
#             access_token = tokens.get('access')
#             refresh_token = tokens.get('refresh')
            
#             # (Optional: Remove in production)
#             print(f"Access Token: {access_token}") 
#             print(f"Refresh Token: {refresh_token}")

#             res = Response()
#             res.data = {'success': True}

#             # Cookie valid for 7 days (in seconds)
#             cookie_age = 7 * 24 * 60 * 60

#             # Set Access Token Cookie
#             res.set_cookie(
#                 key = 'access_token',
#                 value = access_token,
#                 httponly = True,
#                 secure = True, # Should be True in production (requires HTTPS)
#                 samesite = 'None', # Useful for cross-site frontend/backend
#                 path = '/',
#                 max_age=cookie_age, 
#             )

#             # Set Refresh Token Cookie
#             res.set_cookie(
#                 key = 'refresh_token',
#                 value = refresh_token,
#                 httponly = True,
#                 secure = True, # Should be True in production (requires HTTPS)
#                 samesite = 'None',
#                 path = '/',
#                 max_age=cookie_age * 4, # e.g., 28 days
#             )
#             return res
            
#         # except exceptions.AuthenticationFailed as e:
#         #     # Handle specific DRF authentication errors (e.g., bad credentials)
#         #     return Response({'success': False, 'detail': str(e)}, status=401)
        
#         except Exception as e:
#             # Catch any other unexpected exceptions
#             # Improved error response with a status code
#             return Response({'success': False, 'detail': f"An unexpected error occurred: {e}"}, status=500)
      

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
# Import your custom serializer
from .serializer import EmailOrUsernameTokenObtainPairSerializer 
# (assuming you placed the serializer in a 'serializers.py' file)

# class CustomTokenObtainPairView(TokenObtainPairView):
#     # ⭐ Set the custom serializer class
#     serializer_class = EmailOrUsernameTokenObtainPairSerializer 

#     def post(self, request, *args, **kwargs):
#         try:
#             # Calls the custom serializer's validate method
#             response = super().post(request, *args, **kwargs)
            
#             tokens = response.data
#             access_token = tokens.get('access')
#             refresh_token = tokens.get('refresh')
            
#             # (Optional: Remove in production)
#             # print(f"Access Token: {access_token}") 
#             # print(f"Refresh Token: {refresh_token}")

#             res = Response()
#             res.data = {'success': True, 'AccessToken': access_token, 'RefreshToken': refresh_token}

#             # Cookie valid for 28 days (in seconds)
#             cookie_age = 28 * 24 * 60 * 60

#             # Set Access Token Cookie
#             res.set_cookie(
#                 key = 'access_token',
#                 value = access_token,
#                 httponly = True,
#                 # 🔥 FIX 1: Set to False for local HTTP testing
#                 secure = True, 
#                 # 🔥 FIX 2: Set to 'Lax' for safer local testing
#                 samesite = 'None', 
#                 path = '/',
#                 max_age=cookie_age, 
#             )

#             # Set Refresh Token Cookie
#             res.set_cookie(
#                 key = 'refresh_token',
#                 value = refresh_token,
#                 httponly = True,
#                 # 🔥 FIX 1: Set to False for local HTTP testing
#                 secure = True, 
#                 # 🔥 FIX 2: Set to 'Lax' for safer local testing
#                 samesite = 'None',
#                 path = '/',
#                 max_age=cookie_age * 4, # e.g., 28 days
#             )
#             return res
            
#         except Exception as e:
#             # Catch any other unexpected exceptions
#             return Response({'success': False, 'detail': f"An unexpected error occurred: {e}"}, status=500)


# class CustomRefreshTokenView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
#         try:
#             refresh_token = request.COOKIES.get('refresh_token')
#             request.data['refresh'] = refresh_token
#             response = super().post(request, *args, **kwargs)
#             tokens = response.data
#             access_token = tokens.get('access')

#             res = Response()
#             res.data = {'refreshed': True}

#             res.set_cookie(
#                 key='access_token',
#                 value=access_token,
#                 httponly=True,
#                 secure=True,
#                 samesite='None',
#                 path='/'
#             )
#             return res  
#         except:
#             return Response({'refreshed': False})



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer 

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            tokens = response.data
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            res = Response()
            res.data = {'success': True, 'AccessToken': access_token, 'RefreshToken': refresh_token}

            # ✅ Access token valid for 1 day (in seconds)
            access_cookie_age = 1 * 24 * 60 * 60  # 1 day
            
            # ✅ Refresh token valid for 28 days (in seconds)
            refresh_cookie_age = 28 * 24 * 60 * 60  # 28 days

            # Set Access Token Cookie (1 day)
            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True, 
                samesite='None', 
                path='/',
                max_age=access_cookie_age,  # 1 day
            )

            # Set Refresh Token Cookie (28 days)
            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True, 
                samesite='None',
                path='/',
                max_age=refresh_cookie_age,  # 28 days
            )
            return res
            
        except Exception as e:
            return Response({'success': False, 'detail': f"An unexpected error occurred: {e}"}, status=500)


class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if not refresh_token:
                return Response({'refreshed': False, 'detail': 'No refresh token found'}, status=401)
            
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens.get('access')
            new_refresh_token = tokens.get('refresh')  # ✅ New refresh token if rotation enabled

            res = Response()
            res.data = {'refreshed': True}

            # ✅ Update access token cookie
            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=1 * 24 * 60 * 60  # 1 day
            )
            
            # ✅ Update refresh token cookie if rotated
            if new_refresh_token:
                res.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='None',
                    path='/',
                    max_age=28 * 24 * 60 * 60  # 28 days
                )
            
            return res  
        except Exception as e:
            return Response({'refreshed': False, 'detail': str(e)}, status=401)



@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {'success': True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except:
        return Response({'success': False})

from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    print("this is user 1  : ", request.user)
    print("this is now time :: ",timezone.now())
    serializer = UserSerializer(request.user, many=False)
    return Response(serializer.data)
    # return Response({'Authenticated': True})


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .serializer import UserRegisterSerializer, ChangePasswordSerializer

@api_view(['POST'])
@authentication_classes([])  # No auth required
@permission_classes([])      # No permission required
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'User registered successfully!',
            'username': user.username,
            'email': user.email
        })
    else:
        return Response({
            'success': False,
            'errors': serializer.errors
        })



from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash # Important for session-based authentication

# from .serializers import ChangePasswordSerializer

class ChangePasswordView(generics.UpdateAPIView):
    """
    An API view for changing a user's password.
    Requires authentication.
    URL: /api/auth/change-password/ (or similar)
    Method: POST
    Data: { "old_password": "...", "new_password": "...", "confirm_password": "..." }
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated] # Ensures only logged-in users can access this

    def post(self, request, *args, **kwargs):
        # 1. Pass request data and context to the serializer
        serializer = self.get_serializer(data=request.data, context={'request': request})
      
        data = request.data
        print("This is data: ", data)

        # 2. Validate data. If invalid, this raises a 400 Bad Request automatically.
        serializer.is_valid(raise_exception=True)

        # Data is validated, extract the new password
        user = request.user
        new_password = serializer.validated_data['newPassword']

        # 3. Set the new password
        user.set_password(new_password)
        user.save()

        # 4. Update the session hash to prevent the user from being logged out
        # on this device immediately after changing the password.
        update_session_auth_hash(request, user)

        return Response(
            {'message': 'Password updated successfully.'},
            status=status.HTTP_200_OK
        )






# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification
from .serializer import SendOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer

User = get_user_model()

class SendOTPView(APIView):
    """Send OTP to user's email"""
    permission_classes = []  # Allow any user (authenticated or not)
    
    def post(self, request):
        # Delete expired OTPs before processing
        OTPVerification.delete_expired()
        
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_or_phone = serializer.validated_data.get('email_or_phone', '')
        
        # Add type check for safety
        if not isinstance(email_or_phone, str):
            return Response(
                {"error": "Invalid email or phone format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by email
        try:
            if '@' in email_or_phone:
                user = User.objects.get(email=email_or_phone)
            else:
                return Response(
                    {"error": "Phone number verification not implemented yet. Please use email."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate OTP
        otp_code = OTPVerification.generate_otp()
        
        # Save OTP to database
        OTPVerification.objects.create(
            user=user,
            email_or_phone=email_or_phone,
            otp=otp_code
        )
        
        # Send OTP via email
        try:
            send_mail(
                subject='Password Reset OTP',
                message=f'Your OTP for password reset is: {otp_code}\n\nThis OTP is valid for 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_or_phone],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send OTP: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {"message": "OTP sent successfully to your email."},
            status=status.HTTP_200_OK
        )

class VerifyOTPView(APIView):
    """Verify OTP entered by user"""
    permission_classes = []  # Allow any user (authenticated or not)

    def post(self, request):
        # Delete expired OTPs before processing
        OTPVerification.delete_expired()
        
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_or_phone = serializer.validated_data['email_or_phone']
        otp_input = serializer.validated_data['otp']
        
        # Get the latest OTP for this email/phone
        try:
            otp_record = OTPVerification.objects.filter(
                email_or_phone=email_or_phone,
                is_verified=False
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "No OTP request found. Please request a new OTP."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if OTP is expired
        if otp_record.is_expired():
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if max attempts exceeded
        if not otp_record.can_attempt():
            return Response(
                {"error": "Maximum attempts exceeded. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increment attempts
        otp_record.attempts += 1
        otp_record.save()
        
        # Verify OTP
        if otp_record.otp == otp_input:
            otp_record.is_verified = True
            otp_record.save()
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class ResetPasswordView(APIView):
    """Reset password after OTP verification"""
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_or_phone = serializer.validated_data['email_or_phone']
        new_password = serializer.validated_data['new_password']
        
        # Check if OTP was verified
        try:
            otp_record = OTPVerification.objects.filter(
                email_or_phone=email_or_phone,
                is_verified=True
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "Please verify OTP first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if verification is still valid
        if otp_record.is_expired():
            return Response(
                {"error": "OTP verification expired. Please start over."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user and update password
        try:
            if '@' in email_or_phone:
                user = User.objects.get(email=email_or_phone)
            else:
                return Response(
                    {"error": "Invalid email format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Delete all OTP records for this user
        OTPVerification.objects.filter(email_or_phone=email_or_phone).delete()
        
        return Response(
            {"message": "Password reset successfully. You can now login with your new password."},
            status=status.HTTP_200_OK
        )

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_notes(request):
#     user = request.user
#     notes = Note.objects.filter(owner=user)
#     serializer = NoteSerializer(notes, many=True)
#     return Response(serializer.data)

import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Initialize Razorpay client
client = razorpay.Client(auth=(env("RAZORPAY_KEY_ID"), env("RAZORPAY_KEY_SECRET")))

@csrf_exempt
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount_in_rupees = float(data.get("amount"))   # user entered 2222 (₹)
        amount_in_paise = amount_in_rupees * 100     # convert to paise (₹2222 → 222200)

        order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })
        return JsonResponse(order)


import json 

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"]
            })
            return JsonResponse({"status": "Payment Verified"})
        except:
            return JsonResponse({"status": "Payment Verification Failed"}, status=400)





import os
from django.conf import settings
from django.http import HttpResponse, Http404
@permission_classes([IsAuthenticated])
def download_database(request):
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3') # Adjust if your DB path is different

    if os.path.exists(db_path):
        with open(db_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-sqlite3")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(db_path)
            return response
    raise Http404