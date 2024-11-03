from copy import deepcopy
import itertools
from collections import defaultdict, deque

from .constants import BISHOP, KNIGHT
from .pieces import KingPiece, QueenPiece, RookPiece, BishopPiece, KnightPiece, PawnPiece


PIECE_OBJ_TO_NUM = {
    PawnPiece: 1,
    KnightPiece: 2,
    BishopPiece: 3,
    RookPiece: 4,
    QueenPiece: 5,
    KingPiece: 6,
}

STR_TO_PIECE = {
    "q": QueenPiece,
    "r": RookPiece,
    "b": BishopPiece,
    "n": KnightPiece,
}

class ChessBoard:
    def __init__(self) -> None:
        self.player_turn = 1
        self.prev_move = None
        self.castles_allowed = [True, True, True, True] # wq, wk, bq, bk
        self.en_passant_square = -1 # -1 / 0, 1, ..., 63 (- -> -1, a1 -> 0, a2 -> 1, ..., h8 -> 63)
        
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # White Pieces
        self.board[0][0] = RookPiece(1)
        self.board[0][1] = KnightPiece(1)
        self.board[0][2] = BishopPiece(1)
        self.board[0][3] = QueenPiece(1)
        self.board[0][4] = KingPiece(1)
        self.board[0][5] = BishopPiece(1)
        self.board[0][6] = KnightPiece(1)
        self.board[0][7] = RookPiece(1)
    
        for i in range(8):
            self.board[1][i] = PawnPiece(1)
            
        # Black Pieces
        self.board[7][0] = RookPiece(-1)
        self.board[7][1] = KnightPiece(-1)
        self.board[7][2] = BishopPiece(-1)
        self.board[7][3] = QueenPiece(-1)
        self.board[7][4] = KingPiece(-1)
        self.board[7][5] = BishopPiece(-1)
        self.board[7][6] = KnightPiece(-1)
        self.board[7][7] = RookPiece(-1)
        
        for i in range(8):
            self.board[6][i] = PawnPiece(-1)
        
        self.king_pos = {
            1: [0, 4],
            -1: [7, 4],
        }
        
        # hashed history
        self.seen_positions = defaultdict(int)
        self.previous_5_moves = deque([], 5)
    
    def get_all_legal_moves(self):
        moves = []

        for x in range(len(self.board)):
            for y, piece in enumerate(self.board[x]):
                if piece is None or piece.color != self.player_turn:
                    continue
                
                for move in piece.get_all_valid_moves([x, y], self.board, self.castles_allowed, self.player_turn, self.prev_move):
                    temp_test_board = deepcopy(self)
                    
                    if temp_test_board.make_move(*move)[0]:
                        moves.append(move)

        return moves

    def is_check(self):
        king_piece = self.board[self.king_pos[self.player_turn][0]][self.king_pos[self.player_turn][1]]
        for x in range(len(self.board)):
            for y, piece in enumerate(self.board[x]):
                if piece is None or piece.color == self.player_turn:
                    continue

                if piece.is_valid_move([x, y], self.king_pos[self.player_turn], self.board, self.castles_allowed, -self.player_turn, self.prev_move, king_piece):
                    return True
        
        return False
    
    def is_dead_position(self):
        pieces = {
            1: [],
            -1: [],
        }
        
        # get pieces
        for row in self.board:
            for piece in row:
                if piece is not None:
                    pieces[piece.color].append(piece.name)

        piece_count = len(pieces[1]) + len(pieces[-1])
        
        if piece_count > 4:
            return False
        
        if piece_count == 2:
            return True
        
        if piece_count == 4:
            if len(pieces[1]) == len(pieces[-1]) and (KNIGHT in pieces[1] or BISHOP in pieces[1]) and (KNIGHT in pieces[-1] or BISHOP in pieces[-1]):
                return True
            
            return False
        
        player_two_pieces = pieces[1] if len(pieces[1]) == 2 else pieces[-1]
        
        return KNIGHT in player_two_pieces or BISHOP in player_two_pieces
    
    def check_game_over(self): # 1: white win, -1: black win, 2: draw, 0: not game over
        if self.is_dead_position():
            return 2
        
        if self.is_check():
            return -self.player_turn if not self.get_all_legal_moves() else 0
        
        # check for stalemate
        if not self.get_all_legal_moves():
            return 2

        # check for 3-fold-repetition
        return 2 if 3 in self.seen_positions.values() else 0
    
    def make_move(self, start_pos, end_pos, conversion_piece): # conversion_piece: None/q/r/b/n
        """
        Args:
            start_pos (list[int]): start position
            end_pos (list[int]): end position
            conversion_piece (None/q/r/b/n): conversion piece

        Returns:
            Success (boolean): move success
            return_captures (None/(captured_piece.color, captured_piece.name)): captures
            q_castle_move (boolean): queen side castle
            k_castle_move (boolean): king side castle
            en_passant_move (boolean): en passant
            return_conversion (None/q/r/b/n)): conversion
        """
        
        startx, starty = start_pos
        endx, endy = end_pos
        q_castle_move = False
        k_castle_move = False
        en_passant_move = False
        return_conversion = None
        
        if startx > 7 or startx < 0 or starty > 7 or starty < 0 or endx > 7 or endx < 0 or endy > 7 or endy < 0:
            return False, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        piece = self.board[startx][starty]
        end_piece = self.board[endx][endy]
        
        if piece is None:
            return False, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        color = piece.color

        if self.player_turn != color:
            return False, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        if end_piece is not None and end_piece.color == color:
            return False, q_castle_move, k_castle_move, en_passant_move, return_conversion

        if piece.is_valid_move(start_pos, end_pos, self.board, self.castles_allowed, self.player_turn, self.prev_move, end_piece):
            allows_en_passant = isinstance(piece, PawnPiece) and abs(end_pos[0]-start_pos[0]) == 2
            
            # Prevent castle when in check or moving through check
            if isinstance(piece, KingPiece) and abs(end_pos[1]-start_pos[1]) == 2:
                if self.is_check():
                    return False, False, False, False, None
                if end_pos[1] > start_pos[1]: # king side castle
                    self.king_pos[self.player_turn] = [endx, starty+1]

                    if self.is_check():
                        self.king_pos[self.player_turn] = [startx, starty]
                        return False, False, False, False, None
                    
                    self.king_pos[self.player_turn] = [startx, starty]
                else:
                    self.king_pos[self.player_turn] = [endx, starty-1]
                    
                    if self.is_check():
                        self.king_pos[self.player_turn] = [startx, starty]
                        return False, False, False, False, None
                    
                    self.king_pos[self.player_turn] = [startx, starty]
            
            # Update self.king_pos
            if isinstance(piece, KingPiece):
                self.king_pos[self.player_turn] = [endx, endy]
            
            self.board[endx][endy] = piece
            self.board[startx][starty] = None

            if self.is_check():
                # Reset self.king_pos
                if isinstance(piece, KingPiece):
                    self.king_pos[self.player_turn] = [startx, starty]

                self.board[startx][starty] = piece
                self.board[endx][endy] = end_piece
                return False, False, False, False, None
            
            # En Passant Capture
            if (
                isinstance(piece, PawnPiece) and
                self.prev_move and
                self.prev_move[3] and
                abs(end_pos[1]-start_pos[1]) == 1 and
                end_piece is None
            ):
                en_passant_move = True
                self.board[end_pos[0]-self.player_turn][end_pos[1]] = None
            
            # Castle
            if isinstance(piece, KingPiece) and abs(end_pos[1]-start_pos[1]) == 2:
                if end_pos[1] > start_pos[1]: # king side castle
                    k_castle_move = True
                    self.board[start_pos[0]][end_pos[1]-1] = self.board[start_pos[0]][7]
                    self.board[start_pos[0]][7] = None
                else:
                    q_castle_move = True
                    self.board[start_pos[0]][end_pos[1]+1] = self.board[start_pos[0]][0]
                    self.board[start_pos[0]][0] = None
            
            # Update self.castles_allowed
            if isinstance(piece, KingPiece):
                self.castles_allowed[-color+1] = False
                self.castles_allowed[-color+2] = False
            if isinstance(piece, RookPiece) and start_pos == [3.5-color*3.5, 0]: # queen side castle
                self.castles_allowed[-color+1] = False
            if isinstance(piece, RookPiece) and start_pos == [3.5-color*3.5, 7]: # king side castle
                self.castles_allowed[-color+2] = False

            # Conversion
            if isinstance(piece, PawnPiece) and end_pos[0] == 3.5+color*3.5 and conversion_piece in STR_TO_PIECE.keys():
                # print(STR_TO_PIECE[conversion_piece](self.player_turn))
                self.board[endx][endy] = STR_TO_PIECE[conversion_piece](self.player_turn)
                return_conversion = conversion_piece

            # Update self.en_passant_square
            if allows_en_passant:
                enpassant_row = end_pos[0]-self.player_turn
                enpassant_col = end_pos[1]
                self.en_passant_square = 8*enpassant_row + enpassant_col
            else:
                self.en_passant_square = -1

            self.prev_move = (start_pos, end_pos, color, allows_en_passant)
            self.player_turn *= -1

            self.seen_positions[hash(str(self.board))] += 1
            self.previous_5_moves.append(hash(str([start_pos, end_pos])))

            return True, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        return False, q_castle_move, k_castle_move, en_passant_move, return_conversion

    @property
    def integer_board(self):
        return_board = []
        
        for row in self.board:
            return_board.append([])
            for piece in row:
                if piece is None:
                    return_board[-1].append(0)
                else:
                    return_board[-1].append(piece.color*PIECE_OBJ_TO_NUM[type(piece)])

        return return_board
    
    @property
    def ai_input_list(self):
        chess_board = list(itertools.chain(*self.integer_board[::-1])) # [a8, b8, ..., h8, a7, ..., h1]
        chess_board += [
            self.player_turn,
            self.castles_allowed[1], # wk
            self.castles_allowed[0], # wq
            self.castles_allowed[3], # bk
            self.castles_allowed[2], # bq
            self.en_passant_square,
        ]
        return chess_board

    @property
    def non_pawn_piece_count(self):
        count = 0
        
        for row in self.board:
            for piece in row:
                if piece is not None and not isinstance(piece, PawnPiece):
                    count += 1
        
        return count