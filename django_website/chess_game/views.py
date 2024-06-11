from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic.base import TemplateView

from .models import Matchmaking, MultiplayerChessGame


DEFAULT_POSITION = [
    [-4, -2, -3, -5, -6, -3, -2, -4],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [4, 2, 3, 5, 6, 3, 2, 4]

]


class LobbyView(TemplateView):
    template_name = "chess_game/lobby.html"

class MatchmakingView(TemplateView):
    template_name = "chess_game/matchmaking.html"
    
    # def post(self, request, *args, **kwargs):
    #     print(0)
    #     matchmaking = Matchmaking.object()
    #     matchmaking.join(request.user)
    #     print(1)
        
    #     return self.get(HttpRequest())


class ChessGameView(TemplateView):
    template_name = "chess_game/chessboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = MultiplayerChessGame.objects.get(pk=self.kwargs.get("game_id"))
        
        context["game_id"] = game.pk
        context["player_color"] = game.get_user_color(self.request.user)
        
        return context


def move(request):
    if request.POST:
        pass
