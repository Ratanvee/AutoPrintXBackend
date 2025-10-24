from rest_framework_simplejwt.authentication import JWTAuthentication


class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        # print("this is user Access Token : ", request.COOKIES.get('access_token'))
        if not access_token:
            return None
        
        validated_token = self.get_validated_token(access_token)

        try:
            user = self.get_user(validated_token)
            # print("Authenticated..")

        except Exception as e:
            print("Authentication Error occuring : ",e)
            return None
        
        finally:
            print("Authentication Done......")

        return (user, validated_token)

# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
# from rest_framework.exceptions import AuthenticationFailed
# import logging

# logger = logging.getLogger(__name__)

# class CookiesJWTAuthentication(JWTAuthentication):
#     """
#     Custom authentication class that attempts to retrieve the JWT
#     from the 'access_token' cookie first. Falls back to checking the header.
#     """
#     def authenticate(self, request):
#         # 1. Check for 'access_token' in cookies
#         raw_token = request.COOKIES.get('access_token')
#         print("this is tocken getting in CookiesJWTAuthentication : ",raw_token)

#         if raw_token is not None:
            
#             try:
#                 # 1a. Validate the token signature and claims (e.g., expiry)
#                 validated_token = self.get_validated_token(raw_token)
                
#                 # 1b. Retrieve the user (where the failure usually happens)
#                 user = self.get_user(validated_token)
                
#                 # If user is found and active
#                 if user.is_active:
#                     logger.info(f"SUCCESS: User authenticated via cookie: {user.username}")
#                     return (user, validated_token)
#                 else:
#                     raise AuthenticationFailed('User is inactive.')
            
#             except (InvalidToken, TokenError) as e:
#                 # Catches signature failure, token expired, etc.
#                 logger.warning(f"Cookie token validation failed ({type(e).__name__}): {e}. Falling back to header.")
#                 pass
#             except AuthenticationFailed as e:
#                 # Catches user not found or user inactive.
#                 logger.warning(f"Cookie Auth failed (User lookup): {e}. Falling back to header.")
#                 pass
#             except Exception as e:
#                 logger.error(f"Unexpected error during cookie authentication: {e}")
#                 pass
        
#         # 2. Fallback: Check the standard Authorization header (using super())
#         result = super().authenticate(request)
#         if result:
#             logger.info("SUCCESS: User authenticated via Authorization header.")
#         else:
#             logger.warning("FAILURE: Authentication failed via both cookie and header. User is AnonymousUser.")
#         return result

#     def enforce_csrf(self, request):
#         return