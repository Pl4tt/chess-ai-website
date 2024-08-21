import random
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.forms import ValidationError

class ColorChoice(models.IntegerChoices):
    WHITE = 1, "White"
    BLACK = -1, "Black"

class PieceChoice(models.IntegerChoices):
    PAWN = 1, "Pawn"
    KNIGHT = 2, "Knight"
    BISHOP = 3, "Bishop"
    ROOK = 4, "Rook"
    QUEEN = 5, "Queen"
    KING = 6, "King"
    
class ConversionPieceChoice(models.IntegerChoices):
    KNIGHT = 2, "Knight"
    BISHOP = 3, "Bishop"
    ROOK = 4, "Rook"
    QUEEN = 5, "Queen"
    
class WinnerChoice(models.IntegerChoices):
    WHITE = 1, "White"
    BLACK = -1, "Black"
    DRAW = 2, "Draw"
    NONE = 0, "None"
    

class MultiplayerChessGame(models.Model):
    white_player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="white_player", related_name="white_games", on_delete=models.CASCADE, blank=True)
    black_player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="black_player", related_name="black_games", on_delete=models.CASCADE, blank=True)
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="connected_multiplayer_games", blank=True)
    winner = models.IntegerField(choices=WinnerChoice.choices, default=0)
    
    def is_connected(self, user):
        return user in self.connected_users.all()
    
    def update_winner(self, winner):
        if not self.winner:
            print("Winner changed ", self.winner, winner)
            self.winner = winner
    
    def is_white(self, user):
        return user == self.white_player
    
    def is_black(self, user):
        return user == self.black_player
    
    def get_user_color(self, user):
        if not self.check_user(user):
            return None
        return "w" if user == self.white_player else "b"
    
    def join(self, user):
        if not self.is_connected(user):
            self.connected_users.add(user)
            
        self.save()
            
    def leave(self, user):
        if self.is_connected(user):
            self.connected_users.remove(user)
        
        self.save()
    
    def check_user(self, user):
        return user == self.white_player or user == self.black_player
    
    @property
    def get_black_player(self):
        return self.black_player

class AIChessGame(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="player", related_name="ai_games", on_delete=models.CASCADE, blank=True)
    color = models.IntegerField(choices=ColorChoice.choices)
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="connected_ai_games", blank=True)
    winner = models.IntegerField(choices=WinnerChoice.choices, default=0)
    
    def is_connected(self, user):
        return user in self.connected_users.all()
    
    def update_winner(self, winner):
        if not self.winner:
            self.winner = winner

    def is_white(self, user):
        return self.check_user(user) and self.color == 1
    
    def is_black(self, user):
        return self.check_user(user) and self.color == -1
    
    def get_user_color(self, user):
        if not self.check_user(user):
            return None
        return "w" if self.color == 1 else "b"
    
    def get_player_color(self):
        return self.color

    def join(self, user):
        if not self.is_connected(user):
            self.connected_users.add(user)
            
        self.save()
            
    def leave(self, user):
        if self.is_connected(user):
            self.connected_users.remove(user)
        
        self.save()

    def check_user(self, user):
        return user == self.player
    
    @property
    def get_player(self):
        return self.player


class Move(models.Model):
    from_x = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    from_y = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    to_x = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    to_y = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    color = models.IntegerField(choices=ColorChoice.choices)
    conversion_piece = models.IntegerField(choices=ConversionPieceChoice.choices, blank=True, null=True)

class MultiplayerGameMove(Move):
    game = models.ForeignKey(MultiplayerChessGame, verbose_name="game", related_name="moves", on_delete=models.CASCADE)
    
class AIGameMove(Move):
    game = models.ForeignKey(AIChessGame, verbose_name="game", related_name="moves", on_delete=models.CASCADE)


class Matchmaking(models.Model):
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="connected_matchmaking", blank=True)
    
    @classmethod
    def object(cls):
        return cls._default_manager.all().first()
    
    def save(self, *args, **kwargs):
        if not self.pk and Matchmaking.objects.exists():
            raise ValidationError("There can only be one instance of Matchmaking.")

        return super(Matchmaking, self).save(*args, **kwargs)
    
    def is_connected(self, user):
        return user in self.connected_users.all()

    def join(self, user):
        if not self.is_connected(user):
            self.connected_users.add(user)
            
        self.save()
            
    def leave(self, user):
        if self.is_connected(user):
            self.connected_users.remove(user)
        
        self.save()
    
    def connected_users_count(self):
        return len(self.connected_users.all())
    
    def join_game(self):
        lock_id = "join_game_lock"
        lock_acquired = cache.add(lock_id, "locked", 100)
        new_games = []
        
        if lock_acquired:
            try:
                while self.connected_users_count() >= 2:
                    game_type = random.randint(-1, 2) # <0: ai, 0: wait, >0: multiplayer

                    if game_type < 0:
                        new_games.append(self.join_ai_game())
                    elif game_type > 0:
                        new_games.append(self.join_multiplayer_game())
                    else:
                        break
                
                if self.connected_users_count() == 1:
                    game_type = random.randint(-1, 3) # <0: ai, >=0: wait

                    if game_type < 0:
                        new_games.append(self.join_ai_game())

            finally:
                cache.delete(lock_id)
        else:
            print("New game is already being created by another consumer.")
        
        return new_games
    
    def join_multiplayer_game(self):
        user0, user1 = self.connected_users.all()[:2][:]
        self.leave(user0)
        self.leave(user1)
        
        game = MultiplayerChessGame(white_player=user0, black_player=user1)
        game.save()

        return [[user0, user1], game.pk]

    def join_ai_game(self):
        user = self.connected_users.all()[0]
        self.leave(user)
        
        color = -1 if not random.randint(0, 1) else 1
        
        game = AIChessGame(player=user, color=color)
        game.save()

        return [[user], game.pk]
