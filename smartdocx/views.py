# from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.shortcuts import render, HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import time
from rest_framework.permissions import IsAuthenticated, AllowAny

# from .models import Note, CustomUser, UploadFiles, Profile
from .serializer import  UserRegisterSerializer
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

class CustomTokenObtainPairView(TokenObtainPairView):
    # ⭐ Set the custom serializer class
    serializer_class = EmailOrUsernameTokenObtainPairSerializer 

    def post(self, request, *args, **kwargs):
        try:
            # Calls the custom serializer's validate method
            response = super().post(request, *args, **kwargs)
            
            tokens = response.data
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            
            # (Optional: Remove in production)
            # print(f"Access Token: {access_token}") 
            # print(f"Refresh Token: {refresh_token}")

            res = Response()
            res.data = {'success': True, 'AccessToken': access_token, 'RefreshToken': refresh_token}

            # Cookie valid for 28 days (in seconds)
            cookie_age = 28 * 24 * 60 * 60

            # Set Access Token Cookie
            res.set_cookie(
                key = 'access_token',
                value = access_token,
                httponly = True,
                # 🔥 FIX 1: Set to False for local HTTP testing
                secure = True, 
                # 🔥 FIX 2: Set to 'Lax' for safer local testing
                samesite = 'None', 
                path = '/',
                max_age=cookie_age, 
            )

            # Set Refresh Token Cookie
            res.set_cookie(
                key = 'refresh_token',
                value = refresh_token,
                httponly = True,
                # 🔥 FIX 1: Set to False for local HTTP testing
                secure = True, 
                # 🔥 FIX 2: Set to 'Lax' for safer local testing
                samesite = 'None',
                path = '/',
                max_age=cookie_age * 4, # e.g., 28 days
            )
            return res
            
        except Exception as e:
            # Catch any other unexpected exceptions
            return Response({'success': False, 'detail': f"An unexpected error occurred: {e}"}, status=500)


class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens.get('access')

            res = Response()
            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            return res  
        except:
            return Response({'refreshed': False})

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    # print("this is user 1  : ", request.user)
    # serializer = UserSerializer(request.user, many=False)
    # return Response(serializer.data)
    return Response({'Authenticated': True})


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .serializer import UserRegisterSerializer

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

