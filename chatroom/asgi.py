import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatroom.settings')
django.setup()

# This is the ASGI application for Django's HTTP handling.
django_asgi_app = get_asgi_application()

# This is the application wrapped in Django Channels' ProtocolTypeRouter
application = ProtocolTypeRouter({
    "http": django_asgi_app,
})
