from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)

class CookiesJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that attempts to retrieve the JWT
    from the 'access_token' cookie first. Falls back to checking the header.
    """
    def authenticate(self, request):
        # 1. Check for 'access_token' in cookies
        raw_token = request.COOKIES.get('access_token')

        if raw_token is not None:
            
            try:
                # 1a. Validate the token signature and claims (e.g., expiry)
                validated_token = self.get_validated_token(raw_token)
                
                # 1b. Retrieve the user (where the failure usually happens)
                user = self.get_user(validated_token)
                
                # If user is found and active
                if user.is_active:
                    logger.info(f"SUCCESS: User authenticated via cookie: {user.username}")
                    return (user, validated_token)
                else:
                    raise AuthenticationFailed('User is inactive.')
            
            except (InvalidToken, TokenError) as e:
                # Catches signature failure, token expired, etc.
                logger.warning(f"Cookie token validation failed ({type(e).__name__}): {e}. Falling back to header.")
                pass
            except AuthenticationFailed as e:
                # Catches user not found or user inactive.
                logger.warning(f"Cookie Auth failed (User lookup): {e}. Falling back to header.")
                pass
            except Exception as e:
                logger.error(f"Unexpected error during cookie authentication: {e}")
                pass
        
        # 2. Fallback: Check the standard Authorization header (using super())
        result = super().authenticate(request)
        if result:
            logger.info("SUCCESS: User authenticated via Authorization header.")
        else:
            logger.warning("FAILURE: Authentication failed via both cookie and header. User is AnonymousUser.")
        return result

    def enforce_csrf(self, request):
        return
    



# ============================================
# SOLUTION: Cookie-based JWT for WebSocket
# ============================================

# middleware.py - Create this file in your app
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT from cookies
    """
    
    async def __call__(self, scope, receive, send):
        # Get cookies from headers
        headers = dict(scope['headers'])
        cookie_header = headers.get(b'cookie', b'').decode()
        
        logger.info(f"WebSocket connection attempt with cookies: {cookie_header[:100] if cookie_header else 'None'}")
        
        # Parse cookies
        cookies = {}
        if cookie_header:
            for cookie in cookie_header.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
        
        # Get access_token from cookies
        access_token = cookies.get('access_token')
        
        if access_token:
            logger.info(f"Found access_token in cookies: {access_token[:20]}...")
            # Authenticate user
            scope['user'] = await self.get_user_from_token(access_token)
            logger.info(f"Authenticated user: {scope['user']}")
        else:
            logger.warning("No access_token found in cookies")
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Validate JWT token and return user"""
        try:
            # Decode and validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Get user from database
            user = User.objects.get(id=user_id)
            
            if user.is_active:
                logger.info(f"Token validated for user: {user.username}")
                return user
            else:
                logger.warning(f"User {user.username} is inactive")
                return AnonymousUser()
                
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return AnonymousUser()

