from rest_framework.views import APIView
from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializer import UserRegisterSerializer, UserSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.mail import send_mail
from .models import OTPVerification
from .serializer import (
    SendOTPSerializer, 
    VerifyOTPSerializer, 
    ResetPasswordSerializer,
    EmailOrUsernameTokenObtainPairSerializer
)
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from datetime import datetime
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

User = get_user_model()


# ============================================
# HELPER FUNCTIONS
# ============================================

def set_auth_cookies(response, access_token, refresh_token):
    """Centralized cookie setting logic"""
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='None',
        path='/',
        max_age=24 * 60 * 60  # 1 day
    )
    
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='None',
        path='/',
        max_age=28 * 24 * 60 * 60  # 28 days
    )
    return response


def get_cache_key(user_id, endpoint):
    """Generate consistent cache keys"""
    return f"user_{user_id}_{endpoint}_last_modified"


# ============================================
# AUTHENTICATION VIEWS
# ============================================

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            
            res = Response({
                'success': True,
                'AccessToken': tokens.get('access'),
                'RefreshToken': tokens.get('refresh')
            })
            
            return set_auth_cookies(res, tokens.get('access'), tokens.get('refresh'))
            
        except Exception as e:
            return Response(
                {'success': False, 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


import uuid
from .models import WebLoginToken
from rest_framework_simplejwt.tokens import RefreshToken
@api_view(['POST'])
@permission_classes([AllowAny])
def create_web_login_token(request):
    user = request.user

    # Delete all existing WebLoginToken objects associated with this user
    WebLoginToken.objects.filter(user=user).delete()

    token = uuid.uuid4().hex

    WebLoginToken.objects.create(user=user, token=token)

    # base = env("websiteURL")
    base = "https://autoprintx.vercel.app/"
    url = f"{base}autologin?token={token}"


    return Response({"url": url})


# @api_view(['GET'])
# @permission_classes([])
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

class UseWebLoginToken(APIView):
    permission_classes = [AllowAny]   # 🔥 THIS FIXES THE ISSUE

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        if not token:
            return Response({"success": False, "error": "Token missing"}, status=400)

        try:
            # Load all tokens into Python (djongo-safe)
            all_tokens = list(WebLoginToken.objects.all())

            # Manually filter (avoids NOT used SQL bug)
            token_obj = next((t for t in all_tokens if t.token == token and t.used is False), None)

            if token_obj is None:
                return Response({"success": False, "error": "Invalid or used token"}, status=400)

            # mark token used
            token_obj.used = True
            token_obj.save()

            # Create JWT tokens for user
            refresh = RefreshToken.for_user(token_obj.user)

            return Response({
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)



class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {'refreshed': False, 'detail': 'No refresh token found'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            request.data._mutable = True
            request.data['refresh'] = refresh_token
            
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            
            res = Response({'refreshed': True})
            
            # Set new access token
            res.set_cookie(
                key='access_token',
                value=tokens.get('access'),
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=24 * 60 * 60
            )
            
            # Set new refresh token if rotated
            if tokens.get('refresh'):
                res.set_cookie(
                    key='refresh_token',
                    value=tokens.get('refresh'),
                    httponly=True,
                    secure=True,
                    samesite='None',
                    path='/',
                    max_age=28 * 24 * 60 * 60
                )
            
            return res
            
        except Exception as e:
            return Response(
                {'refreshed': False, 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(['POST'])
def logout(request):
    """Logout and clear cookies"""
    res = Response({'success': True})
    res.delete_cookie('access_token', path='/', samesite='None')
    res.delete_cookie('refresh_token', path='/', samesite='None')
    
    # Clear user cache on logout
    if request.user.is_authenticated:
        cache_pattern = f"user_{request.user.id}_*"
        if cache_pattern:
            cache.delete(cache_pattern)
    
    return res


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    """Check authentication status with user data"""
    serializer = UserSerializer(request.user, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):
    """User registration"""
    serializer = UserRegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'User registered successfully!',
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# PASSWORD MANAGEMENT
# ============================================

class ChangePasswordView(APIView):
    """Change password for authenticated users"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        new_password = serializer.validated_data['newPassword']
        
        user.set_password(new_password)
        user.save()
        
        # Keep user logged in after password change
        update_session_auth_hash(request, user)
        
        return Response(
            {'message': 'Password updated successfully.'},
            status=status.HTTP_200_OK
        )



class SendOTPView(APIView):
    """Send OTP to user's email for password reset or email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Clean up expired OTPs first
        # OTPVerification.delete_expired()
         # Delete expired OTPs (only saved ones)
        OTPVerification.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        # Validate request data
        serializer = SendOTPSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Extract the first error message
            errors = serializer.errors
            
            # Get the first error from any field
            if 'email_or_phone' in errors:
                error_message = errors['email_or_phone'][0] if isinstance(errors['email_or_phone'], list) else str(errors['email_or_phone'])
            elif 'non_field_errors' in errors:
                error_message = errors['non_field_errors'][0] if isinstance(errors['non_field_errors'], list) else str(errors['non_field_errors'])
            else:
                error_message = "Invalid request data."
            
            return Response(
                {
                    "success": False,
                    "error": error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get validated data
        email_or_phone = serializer.validated_data['email_or_phone']
        purpose = serializer.validated_data.get('purpose', 'forgot_password')
        
        # Get user (will be None for signup)
        user = None
        if purpose == 'forgot_password':
            try:
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "error": "No account found with this email."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Delete any previous unverified OTPs for this email/purpose
        # FIXED: Use Python filtering instead of database query with is_verified=False
        try:
            old_otps = OTPVerification.objects.filter(
                email_or_phone=email_or_phone,
                purpose=purpose
            )
            
            # Delete unverified OTPs in Python instead of database query
            for otp in old_otps:
                if not otp.is_verified:
                    otp.delete()
        except Exception as e:
            print(f"Error deleting old OTPs: {e}")
        
        # Generate and save new OTP
        otp_code = OTPVerification.generate_otp()
        otp_obj = OTPVerification.objects.create(
            user=user,  # None for signup
            email_or_phone=email_or_phone,
            otp=otp_code,
            purpose=purpose
        )
        
        # Prepare email content based on purpose
        if purpose == 'signup':
            email_subject = 'Email Verification Code'
            email_message = f'''Welcome!

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you did not request this verification, please ignore this email.

Best regards,
Your App Team'''
        else:  # forgot_password
            email_subject = 'Password Reset Code'
            email_message = f'''Hello,

Your password reset code is: {otp_code}

This code will expire in 10 minutes.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
Your App Team'''
        
        # Send OTP email
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_or_phone],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error for debugging
            print(f"Email sending error: {str(e)}")
            
            # Delete the OTP since email failed
            otp_obj.delete()
            
            return Response(
                {
                    "success": False,
                    "error": "Failed to send OTP. Please check your email address and try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Success response
        message = "Verification code sent to your email." if purpose == 'signup' else "Password reset code sent to your email."
        
        return Response(
            {
                "success": True,
                "message": message
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    """Verify OTP for password reset"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        OTPVerification.delete_expired()
        
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_or_phone = serializer.validated_data['email_or_phone']
        otp_input = serializer.validated_data['otp']
        
        try:
            # Get all OTP records for this email, ordered by latest first
            otp_records = OTPVerification.objects.filter(
                email_or_phone=email_or_phone
            ).order_by('-created_at')
            
            # Find the first unverified OTP
            otp_record = None
            for record in otp_records:
                if not record.is_verified:
                    otp_record = record
                    break
            
            if otp_record is None:
                raise OTPVerification.DoesNotExist
                
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "No OTP request found. Please request a new OTP."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if otp_record.is_expired():
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp_record.can_attempt():
            return Response(
                {"error": "Maximum attempts exceeded. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        otp_record.attempts += 1
        
        if otp_record.otp == otp_input:
            otp_record.is_verified = True
            otp_record.save()
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK
            )
        
        otp_record.save()
        return Response(
            {"error": f"Invalid OTP. {otp_record.max_attempts - otp_record.attempts} attempts remaining."},
            status=status.HTTP_400_BAD_REQUEST
        )



class ResetPasswordView(APIView):
    """Reset password after OTP verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_or_phone = serializer.validated_data['email_or_phone']
        new_password = serializer.validated_data['new_password']
        
        # FIXED: Get all OTP records and filter in Python
        try:
            otp_records = OTPVerification.objects.filter(
                email_or_phone=email_or_phone
            ).order_by('-created_at')
            
            # Find the first verified OTP
            otp_record = None
            for record in otp_records:
                if record.is_verified:
                    otp_record = record
                    break
            
            if otp_record is None:
                raise OTPVerification.DoesNotExist
                
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "Please verify OTP first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if otp_record.is_expired():
            return Response(
                {"error": "OTP verification expired. Please start over."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        try:
            user = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user.set_password(new_password)
        user.save()
        
        # Clean up OTP records - Delete one by one to avoid Djongo issues
        try:
            otps_to_delete = OTPVerification.objects.filter(email_or_phone=email_or_phone)
            for otp in otps_to_delete:
                otp.delete()
        except Exception as e:
            print(f"Error deleting OTP records: {e}")
            # Continue anyway, password is already reset
        
        return Response(
            {"message": "Password reset successfully. You can now login with your new password."},
            status=status.HTTP_200_OK
        )

# ============================================
# PAYMENT INTEGRATION
# ============================================

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(env("RAZORPAY_KEY_ID"), env("RAZORPAY_KEY_SECRET"))
)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create Razorpay order"""
    try:
        amount_in_rupees = float(request.data.get("amount", 0))
        
        if amount_in_rupees <= 0:
            return Response(
                {"error": "Invalid amount"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount_in_paise = int(amount_in_rupees * 100)
        
        order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })
        
        return Response(order, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
# UTILITY ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_database(request):
    """Download database file (admin only)"""
    if not request.user.is_staff:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    import os
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    
    if not os.path.exists(db_path):
        return Response(
            {"error": "Database file not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    with open(db_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/x-sqlite3")
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(db_path)}'
        return response