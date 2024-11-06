import django
import os
from decouple import config
django.setup()

import chess_game.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{config("PROJECT_NAME")}.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AllowedHostsOriginValidator( 
        AuthMiddlewareStack(
            URLRouter(
                chess_game.routing.websocket_urlpatterns
            )
        )
    )
})