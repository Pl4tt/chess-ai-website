from django.urls import path

from . import views

app_name = "chess_game"
urlpatterns = [
    path("", views.LobbyView.as_view(), name="lobby"),
    path("matchmaking", views.MatchmakingView.as_view(), name="matchmaking"),
    path("<int:game_id>/", views.ChessGameView.as_view(), name="chessboard"),
]