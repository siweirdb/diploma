from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<receiver_id>[0-9a-fA-F-]+)/$", ChatConsumer.as_asgi()),
]
