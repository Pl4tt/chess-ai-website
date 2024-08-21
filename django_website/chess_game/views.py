from django.http import Http404
from django.views.generic.base import TemplateView

from .constants import ALLOWED_TYPES
from .url_encryption import decrypt
from .models import AIChessGame, MultiplayerChessGame


class LobbyView(TemplateView):
    template_name = "chess_game/lobby.html"

class MatchmakingView(TemplateView):
    template_name = "chess_game/matchmaking.html"

class ChessGameView(TemplateView):
    template_name = "chess_game/chessboard.html"
    allowed_types = ALLOWED_TYPES
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game_string = decrypt(self.kwargs.get("encrypted_game", "error-404"))
        split_game_string = game_string.split("-")
        
        self.game_type, self.game_id = split_game_string[0], int(split_game_string[1])
        
        print(self.game_type)
        print(self.game_id)
        
        if not self.game_type in self.allowed_types:
            raise Http404()
        
        if self.game_type == "multiplayer":
            game = MultiplayerChessGame.objects.get(pk=self.game_id)
        else:
            game = AIChessGame.objects.get(pk=self.game_id)
        
        context["game_id"] = game.pk
        context["player_color"] = game.get_user_color(self.request.user)
        context["game_type"] = self.game_type
        
        return context

