from copy import deepcopy
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.urls import reverse
from django.contrib.staticfiles import finders
import torch
from torchsummary import summary

from account.models import Account
from .url_encryption import encrypt

from .constants import ALLOWED_TYPES, NUM_TO_PIECE, PIECE_TO_NUM, SQUARE_TO_COORDINATE
from .board import STR_TO_PIECE, ChessBoard
from .models import AIChessGame, AIGameMove, Matchmaking, MultiplayerChessGame, MultiplayerGameMove
from .pytorch_modules import ChessNet, choose_move


class ChessGameConsumer(AsyncWebsocketConsumer):
    """
    receive(): json input of form (a, b, c, d: Integers):
    {
        'command': 'move',
        'move': {
            'start': [a, b],
            'end': [c, d],
            'conversion' (optional): q/r/b/n
        },
        'color': color,
        'pieceType': pieceType,
        'username': username
    }
    """
    allowed_types = ALLOWED_TYPES
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = ChessBoard()

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_room_type = self.scope["url_route"]["kwargs"]["game_type"]
        self.room_group_name = f"game_{self.game_room_type}_{self.room_name}"
        self.user = self.scope["user"]
        
        if not self.game_room_type in self.allowed_types:
            self.close()
        
        try:
            if self.game_room_type == "multiplayer":
                game = await sync_to_async(MultiplayerChessGame.objects.get, thread_sensitive=True)(pk=self.room_name)
            else:
                game = await sync_to_async(AIChessGame.objects.get, thread_sensitive=True)(pk=self.room_name)
                filepath = finders.find("ai_model/model_20241103_003053_29")
                self.ai_model = ChessNet()
                self.ai_model.load_state_dict(torch.load(filepath, map_location=torch.device('cpu')))
                self.ai_model.eval()
                print(summary(self.ai_model, input_size=(6, 8, 8)))

            self.game_room = game
        except MultiplayerChessGame.DoesNotExist:
            await self.close()

        is_member = await sync_to_async(self.game_room.check_user, thread_sensitive=True)(self.user)
        if not is_member:
            self.color = 0
        else:
            self.color = 1 if self.game_room.is_white(self.user) else -1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        
        await self.accept()
        await sync_to_async(self.game_room.join, thread_sensitive=True)(self.user.pk)

        await self.load_position()

        if self.game_room_type == "ai" and self.color != self.board.player_turn:
            pass
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_position",
                "board": self.board.integer_board,
                "username": self.user.username,
                "winner": self.game_room.winner,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        await sync_to_async(self.game_room.leave, thread_sensitive=True)(self.user)

    @sync_to_async
    def load_position(self):
        moves = self.game_room.moves.all()
        
        for move in moves:
            
            move_feedback = self.board.make_move([move.from_x, move.from_y], [move.to_x, move.to_y], NUM_TO_PIECE.get(move.conversion_piece))
            print(move_feedback)

    async def receive(self, text_data):
        print(self.board.board)
        text_data_json = json.loads(text_data)
        command = text_data_json.get("command")

        if command == "move":
            move = text_data_json.get("move")
            username = text_data_json.get("username")
            
            if username != self.user.username:
                await self.disconnect(close_code=4003)
                return

            if not self.color:
                return
            
            if self.game_room.winner != 0:
                return
            
            if move is not None:
                startx = int(move["start"][0])-1
                starty = SQUARE_TO_COORDINATE.get(move["start"][1])-1
                endx = int(move["end"][0])-1
                endy = SQUARE_TO_COORDINATE.get(move["end"][1])-1
                conversion_piece = move.get("conversionPiece", None)

                await self.execute_new_move_chain([[startx, starty], [endx, endy], conversion_piece], self.color)

        elif command == "make_ai_move_if_possible":
            username = text_data_json.get("username")
            
            if username != self.user.username:
                await self.disconnect(close_code=4003)
                return
            
            if not self.color:
                print(1)
                return

            await self.make_ai_move_if_possible()

    async def send_position(self, event):
        board = event["board"]
        username = event["username"]
        winner = event["winner"]
        
        await self.send(json.dumps({
            "command": "initiate_position",
            "board": board,
            "username": username,
            "winner": winner,
        }))

    @sync_to_async
    def update_board(self, event):
        move = event["move"]
        color = event["color"]
        num_color = 1 if color == "w" else -1
        username = event["username"]
        user = Account.objects.get(username=username)
        
        if self.game_room.get_user_color(user) is None:
            self.disconnect(close_code=4003)
            return

        startx = move["start"][0]
        starty = move["start"][1]
        endx = move["end"][0]
        endy = move["end"][1]
        conversion_piece = move.get("conversionPiece")

        if (
            self.board.prev_move != ([startx, starty], [endx, endy], num_color, True) and
            self.board.prev_move != ([startx, starty], [endx, endy], num_color, False)
        ):
            self.board.make_move([startx, starty], [endx, endy], conversion_piece)

    async def move_made(self, event):
        move = event["move"]
        color = event["color"]
        piece_type = event["pieceType"]
        username = event["username"]
        winner = event["winner"]
        print(color, piece_type)

        await self.send(json.dumps({
            "command": "make_move",
            "move": move,
            "color": color,
            "pieceType": piece_type,
            "username": username,
            "winner": winner,
        }))

    async def make_ai_move_if_possible(self):
        if self.game_room_type != "ai" or self.board.player_turn == self.game_room.get_player_color():
            return
        
        with torch.no_grad():
            chosen_move = choose_move(self.ai_model, self.board, self.board.player_turn)
        print(chosen_move)
        move_res = await self.execute_new_move_chain(chosen_move, -self.color)
        print(move_res)
        print("done :)")
    
    async def execute_new_move_chain(self, move, colorint):
        board_move = self.board.make_move(*move)
        startx, starty = move[0]
        endx, endy = move[1]
        conversion_piece = move[2]
        colorstr = "w" if colorint == 1 else "b"

        if board_move[0]:
            if conversion_piece in STR_TO_PIECE.keys():
                piece_type = "p"
                if self.game_room_type == "multiplayer":
                    db_move = MultiplayerGameMove(
                        from_x=startx,
                        from_y=starty,
                        to_x=endx,
                        to_y=endy,
                        color=colorint,
                        conversion_piece=PIECE_TO_NUM[conversion_piece],
                        game=self.game_room
                    )
                else:
                    db_move = AIGameMove(
                        from_x=startx,
                        from_y=starty,
                        to_x=endx,
                        to_y=endy,
                        color=colorint,
                        conversion_piece=PIECE_TO_NUM[conversion_piece],
                        game=self.game_room
                    )
            else:
                piece_type = self.board.board[endx][endy].name
                if self.game_room_type == "multiplayer":
                    db_move = MultiplayerGameMove(
                        from_x=startx,
                        from_y=starty,
                        to_x=endx,
                        to_y=endy,
                        color=colorint,
                        game=self.game_room
                    )
                else:
                    db_move = AIGameMove(
                        from_x=startx,
                        from_y=starty,
                        to_x=endx,
                        to_y=endy,
                        color=colorint,
                        game=self.game_room
                    )
            await sync_to_async(db_move.save, thread_sensitive=True)()

            winner = self.board.check_game_over()
            self.game_room.update_winner(winner)
            await sync_to_async(self.game_room.save, thread_sensitive=True)()
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "move_made",
                    "move": {
                        "start": [startx, starty],
                        "end": [endx, endy],
                        "qCastle": board_move[1],
                        "kCastle": board_move[2],
                        "enPassant": board_move[3],
                        "conversion": board_move[4],
                    },
                    "color": colorstr,
                    "pieceType": piece_type,
                    "username": self.user.username,
                    "winner": self.game_room.winner,
                }
            )
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update_board",
                    "move": {
                        "start": [startx, starty],
                        "end": [endx, endy],
                        "conversionPiece": board_move[4],
                    },
                    "color": colorstr,
                    "username": self.user.username,
                    "winner": self.game_room.winner,
                }
            )
            
            return True
        
        return False
        

class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        try:
            self.matchmaking = await sync_to_async(Matchmaking.object, thread_sensitive=True)()
        except Matchmaking.DoesNotExist:
            await sync_to_async(Matchmaking.objects.create, thread_sensitive=True)()
        finally:
            self.matchmaking = await sync_to_async(Matchmaking.object, thread_sensitive=True)()

        self.room_name = self.matchmaking.pk
        self.room_group_name = f"matchmaking_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        
        await self.accept()
        await sync_to_async(self.matchmaking.join, thread_sensitive=True)(self.user)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "try_join_game",
            }
        )
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        await sync_to_async(self.matchmaking.leave, thread_sensitive=True)(self.user)

    async def try_join_game(self, event):
        new_games = await sync_to_async(self.matchmaking.join_game, thread_sensitive=True)()

        for game in new_games:
            users, game_id = game
            
            if len(users) == 2: # multiplayer game
                encrypted_game = encrypt(f"multiplayer-{game_id}")

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_connection",
                        "game_url": reverse("chess_game:chessboard", args=[encrypted_game]),
                        "user1_username": users[0].username,
                        "user2_username": users[1].username
                    }
                )
            elif len(users) == 1: # ai game
                encrypted_game = encrypt(f"ai-{game_id}")

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "ai_game_connection",
                        "game_url": reverse("chess_game:chessboard", args=[encrypted_game]),
                        "user_username": users[0].username
                    }
                )
        
        if not new_games:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "waiting_signal",
                    "user_username": self.user.username
                }
            )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json.get("command")

        if command == "retry_join_game":
            username = text_data_json.get("username")
            
            if username != self.user.username:
                await self.disconnect(close_code=4003)
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "try_join_game",
                }
            )

    async def game_connection(self, event):
        game_url = event["game_url"]
        user1_username = event["user1_username"]
        user2_username = event["user2_username"]
        
        if user1_username == self.user.username or user2_username == self.user.username:
            await self.send(json.dumps({
                "command": "join_game",
                "gameUrl": game_url,
            }))
            await self.close()

    async def ai_game_connection(self, event):
        game_url = event["game_url"]
        user_username = event["user_username"]

        if user_username == self.user.username:
            await self.send(json.dumps({
                "command": "join_game",
                "gameUrl": game_url,
            }))
            await self.close()
        
    async def waiting_signal(self, event):
        user_username = event["user_username"]

        if user_username == self.user.username:
            await self.send(json.dumps({
                "command": "wait_for_game"
            }))