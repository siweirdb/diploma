import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foundly.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middleware import JWTAuthMiddlewareStack  # Import the middleware
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
