import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.urls import reverse

from account.models import Account

from .constants import PIECE_TO_NUM, SQUARE_TO_COORDINATE
from .board import ChessBoard
from .models import Matchmaking, MultiplayerGameCapture, MultiplayerChessGame, MultiplayerGameMove


class ChessGameConsumer(AsyncWebsocketConsumer):
    """
    receive(): json input of form (a, b, c, d: Integers):
    {
        'type': 'move_made',
        'move': {
            'start': [a, b],
            'end': [c, d]
        },
        "color": color,
        "pieceType": pieceType,
        'username': username
    }
    """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = ChessBoard()

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"game_{self.room_name}"
        self.user = self.scope["user"]
        
        try:
            game = await sync_to_async(MultiplayerChessGame.objects.get, thread_sensitive=True)(pk=self.room_name)
            self.game_room = game
        except MultiplayerChessGame.DoesNotExist:
            await self.close()

        is_member = await sync_to_async(self.game_room.check_user, thread_sensitive=True)(self.user)
        if not is_member:
            await self.close()
            
        self.color = 1 if self.game_room.is_white(self.user) else -1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        
        await self.accept()
        await sync_to_async(self.game_room.join, thread_sensitive=True)(self.user.pk)

        await self.load_position()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_position",
                "board": self.board.integer_board,
                "username": self.user.username
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
            move_feedback = self.board.make_move([move.from_x, move.from_y], [move.to_x, move.to_y])
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

            if move is not None:
                startx = int(move["start"][0])-1
                starty = SQUARE_TO_COORDINATE.get(move["start"][1])-1
                endx = int(move["end"][0])-1
                endy = SQUARE_TO_COORDINATE.get(move["end"][1])-1
                board_move = self.board.make_move([startx, starty], [endx, endy])
                print(board_move)
                if board_move[0]:
                    color = text_data_json["color"]
                    piece_type = text_data_json["pieceType"]
                    db_move = MultiplayerGameMove(
                        from_x=startx,
                        from_y=starty,
                        to_x=endx,
                        to_y=endy,
                        color=self.color,
                        game=self.game_room
                    )
                    await sync_to_async(db_move.save, thread_sensitive=True)()
                    
                    if board_move[1] is not None:
                        db_capture = MultiplayerGameCapture(
                            captured_piece=PIECE_TO_NUM[board_move[1][1]],
                            color=board_move[1][0],
                            game=self.game_room
                        )
                        await sync_to_async(db_capture.save, thread_sensitive=True)()
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "move_made",
                            "move": {
                                "start": [startx, starty],
                                "end": [endx, endy],
                                "qCastle": board_move[2],
                                "kCastle": board_move[3],
                                "enPassant": board_move[4],
                            },
                            "color": color,
                            "pieceType": piece_type,
                            "username": username
                        }
                    )
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "update_board",
                            "move": {
                                "start": [startx, starty],
                                "end": [endx, endy]
                            },
                            "color": color,
                            "username": username
                        }
                    )

    async def send_position(self, event):
        board = event["board"]
        username = event["username"]
        
        await self.send(json.dumps({
            "command": "initiate_position",
            "board": board,
            "username": username,
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

        if (
            self.board.prev_move != ([startx, starty], [endx, endy], num_color, True) and
            self.board.prev_move != ([startx, starty], [endx, endy], num_color, False)
        ):
            self.board.make_move([startx, starty], [endx, endy])

    async def move_made(self, event):
        move = event["move"]
        color = event["color"]
        piece_type = event["pieceType"]
        username = event["username"]
        print(color, piece_type)
        await self.send(json.dumps({
            "command": "make_move",
            "move": move,
            "color": color,
            "pieceType": piece_type,
            "username": username,
        }))


class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
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
                "type": "new_connection",
            }
        )
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        await sync_to_async(self.matchmaking.leave, thread_sensitive=True)(self.user)

    async def new_connection(self, event):
        if await sync_to_async(self.matchmaking.connected_users_count, thread_sensitive=True)() >= 2:
            mm_response = await sync_to_async(self.matchmaking.join_game, thread_sensitive=True)()
            
            if mm_response is not None:
                users, game_id = mm_response
                if users[0].pk == self.user.pk or users[1].pk == self.user.pk:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "game_connection",
                            "game_url": reverse("chess_game:chessboard", args=[game_id]),
                            "user1_username": users[0].username,
                            "user2_username": users[1].username
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