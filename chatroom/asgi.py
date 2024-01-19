import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumer import ChatConsumer
from channels.http import AsgiHandler
from channels.staticfiles import AsgiStaticFilesHandler
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatroom.settings')

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/", ChatConsumer.as_asgi()),
        ])
    ),
    "http": AsgiHandler(
        URLRouter([
            path("static/", AsgiStaticFilesHandler(directory="static")),  # Assuming static files are in a "static" directory
        ])
    ),
})
