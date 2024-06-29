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
    
    def is_check(self):
        king_piece = self.board[self.king_pos[self.player_turn][0]][self.king_pos[self.player_turn][1]]
        for x in range(len(self.board)):
            for y, piece in enumerate(self.board[x]):
                if piece is None or piece.color == self.player_turn:
                    continue

                if piece.is_valid_move([x, y], self.king_pos[self.player_turn], self.board, self.castles_allowed, -self.player_turn, self.prev_move, king_piece):
                    return True
        
        return False
    
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
        return_captures = None
        q_castle_move = False
        k_castle_move = False
        en_passant_move = False
        return_conversion = None
        
        if startx > 7 or startx < 0 or starty > 7 or starty < 0 or endx > 7 or endx < 0 or endy > 7 or endy < 0:
            return False, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        piece = self.board[startx][starty]
        end_piece = self.board[endx][endy]
        
        if piece is None:
            return False, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        color = piece.color

        if self.player_turn != color:
            return False, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        if end_piece is not None and end_piece.color == color:
            return False, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        if piece.is_valid_move(start_pos, end_pos, self.board, self.castles_allowed, self.player_turn, self.prev_move, end_piece):
            if end_piece is not None:
                return_captures = (end_piece.color, end_piece.name)
            allows_en_passant = isinstance(piece, PawnPiece) and abs(end_pos[0]-start_pos[0]) == 2
            
            if isinstance(piece, KingPiece) and abs(end_pos[1]-start_pos[1]) == 2 and self.is_check():
                return False, None, False, False, False, None
            
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
                return False, None, False, False, False, None
            
            # En Passant Capture
            if (
                isinstance(piece, PawnPiece) and
                self.prev_move and
                self.prev_move[3] and
                abs(end_pos[1]-start_pos[1]) == 1 and
                end_piece is None
            ):
                en_passant_move = True
                captured_piece = self.board[end_pos[0]-self.player_turn][end_pos[1]]
                return_captures = (captured_piece.color, captured_piece.name)
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
            print(conversion_piece)
            if conversion_piece in STR_TO_PIECE.keys():
                print(STR_TO_PIECE[conversion_piece](self.player_turn))
                self.board[endx][endy] = STR_TO_PIECE[conversion_piece](self.player_turn)
                return_conversion = conversion_piece

            self.prev_move = (start_pos, end_pos, color, allows_en_passant)
            self.player_turn *= -1

            return True, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion
        
        return False, return_captures, q_castle_move, k_castle_move, en_passant_move, return_conversion

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
        