from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chess/matchmaking/$", consumers.MatchmakingConsumer.as_consumer()),
    re_path(r"ws/chess/(?P<game_type>\w+)/(?P<game_id>\w+)/$", consumers.ChessGameConsumer.as_consumer()),
    re_path(r"ws/chess/abc/$", consumers.ChessGameConsumer.as_consumer()),
]