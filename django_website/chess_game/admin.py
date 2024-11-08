from django.contrib import admin

from .models import Matchmaking, MultiplayerChessGame, MultiplayerGameMove, AIChessGame, AIGameMove


@admin.register(MultiplayerChessGame)
class MultiplayerChessGameAdmin(admin.ModelAdmin):
    list_display = ("id", "white_player", "black_player", "winner")
    list_display_links = ("id", "white_player", "black_player", "winner")
    readonly_fields = ("id",)
    list_filter = ("white_player", "black_player")
    search_fields = ("id", "white_player", "black_player")

@admin.register(MultiplayerGameMove)
class MultiplayerGameMoveAdmin(admin.ModelAdmin):
    list_display = ("id", "from_x", "from_y", "to_x", "to_y", "color", "game")
    list_display_links = ("id", "from_x", "from_y", "to_x", "to_y", "color", "game")
    readonly_fields = ("id",)
    list_filter = ("from_x", "from_y", "to_x", "to_y", "color", "game")
    search_fields = ("id", "from_x", "from_y", "to_x", "to_y", "color")

@admin.register(AIChessGame)
class AIChessGameAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "winner")
    list_display_links = ("id", "player", "winner")
    readonly_fields = ("id",)
    list_filter = ("player",)
    search_fields = ("id", "player")

@admin.register(AIGameMove)
class AIGameMoveAdmin(admin.ModelAdmin):
    list_display = ("id", "from_x", "from_y", "to_x", "to_y", "color", "game")
    list_display_links = ("id", "from_x", "from_y", "to_x", "to_y", "color", "game")
    readonly_fields = ("id",)
    list_filter = ("from_x", "from_y", "to_x", "to_y", "color", "game")
    search_fields = ("id", "from_x", "from_y", "to_x", "to_y", "color")

@admin.register(Matchmaking)
class MatchmakingAdmin(admin.ModelAdmin):
    list_display = ("id",)
    list_display_links = ("id",)
    readonly_fields = ("id",)
    search_fields = ("id",)

