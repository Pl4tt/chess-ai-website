from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chess/matchmaking/$", consumers.MatchmakingConsumer.as_asgi()),
    re_path(r"ws/chess/(?P<game_id>\w+)/$", consumers.ChessGameConsumer.as_asgi()),
    re_path(r"ws/chess/abc/$", consumers.ChessGameConsumer.as_asgi()),
]