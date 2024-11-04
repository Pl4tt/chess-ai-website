import django
django.setup()

import chess_game.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

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