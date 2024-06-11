from django.contrib import admin

from .models import Matchmaking, MultiplayerChessGame, MultiplayerGameMove, MultiplayerGameCapture, AIChessGame, AIGameMove, AIGameCapture


@admin.register(MultiplayerChessGame)
class MultiplayerChessGameAdmin(admin.ModelAdmin):
    list_display = ("id", "white_player", "black_player")
    list_display_links = ("id", "white_player", "black_player")
    readonly_fields = ("id",)
    list_filter = ("white_player", "black_player")
    search_fields = ("id", "white_player", "black_player")

@admin.register(MultiplayerGameMove)
class MultiplayerGameMoveAdmin(admin.ModelAdmin):
    list_display = ("id", "from_x", "from_y", "to_x", "to_y", "color")
    list_display_links = ("id", "from_x", "from_y", "to_x", "to_y", "color")
    readonly_fields = ("id",)
    list_filter = ("from_x", "from_y", "to_x", "to_y", "color")
    search_fields = ("id", "from_x", "from_y", "to_x", "to_y", "color")

@admin.register(MultiplayerGameCapture)
class MultiplayerGameCaptureAdmin(admin.ModelAdmin):
    list_display = ("id", "captured_piece", "color")
    list_display_links = ("id", "captured_piece", "color")
    readonly_fields = ("id",)
    list_filter = ("captured_piece", "color")
    search_fields = ("id", "captured_piece", "color")

@admin.register(AIChessGame)
class AIChessGameAdmin(admin.ModelAdmin):
    list_display = ("id", "player")
    list_display_links = ("id", "player")
    readonly_fields = ("id",)
    list_filter = ("player",)
    search_fields = ("id", "player")

@admin.register(AIGameMove)
class AIGameMoveAdmin(admin.ModelAdmin):
    list_display = ("id", "from_x", "from_y", "to_x", "to_y", "color")
    list_display_links = ("id", "from_x", "from_y", "to_x", "to_y", "color")
    readonly_fields = ("id",)
    list_filter = ("from_x", "from_y", "to_x", "to_y", "color")
    search_fields = ("id", "from_x", "from_y", "to_x", "to_y", "color")

@admin.register(AIGameCapture)
class AIGameCaptureAdmin(admin.ModelAdmin):
    list_display = ("id", "captured_piece", "color")
    list_display_links = ("id", "captured_piece", "color")
    readonly_fields = ("id",)
    list_filter = ("captured_piece", "color")
    search_fields = ("id", "captured_piece", "color")

@admin.register(Matchmaking)
class MatchmakingAdmin(admin.ModelAdmin):
    list_display = ("id",)
    list_display_links = ("id",)
    readonly_fields = ("id",)
    search_fields = ("id",)

