from django.urls import re_path
from ownerside.consumers import MyConsumer, OrdersOverviewConsumer

websocket_urlpatterns = [
    re_path(r'ws/somepath/$', MyConsumer.as_asgi()),
    re_path(r'ws/orders-overview/$', OrdersOverviewConsumer.as_asgi()),
]