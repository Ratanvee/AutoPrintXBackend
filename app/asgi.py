# """
# ASGI config for app project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# application = get_asgi_application()


# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from smartdocx.routing import websocket_urlpatterns

# application = ProtocolTypeRouter({
#     # "http": get_default_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })


# ============================================
# asgi.py - Update to use the middleware
# ============================================

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Initialize Django ASGI application first
django_asgi_app = get_asgi_application()

# Import after Django is initialized
# from your_app import routing
from smartdocx.authentication import JWTAuthMiddleware
from smartdocx.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(  # Use our custom JWT middleware
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})

