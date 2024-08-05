from .constants import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN


def validate_bishop_move(start_pos, end_pos, board):
    if end_pos[0]-start_pos[0] == end_pos[1]-start_pos[1]: # top left & bottom right
        oriented_distance = end_pos[0]-start_pos[0]
        orientation = oriented_distance//abs(oriented_distance)
        for i in range(orientation, oriented_distance, orientation):
            if board[start_pos[0]+i][start_pos[1]+i] is not None:
                return False
    elif end_pos[0]-start_pos[0] == start_pos[1]-end_pos[1]: # to right & bottom left
        oriented_distance = end_pos[0]-start_pos[0]
        orientation = oriented_distance//abs(oriented_distance)
        for i in range(orientation, oriented_distance, orientation):
            if board[start_pos[0]+i][start_pos[1]-i] is not None:
                return False
    else:
        return False
    return True

def validate_rook_move(start_pos, end_pos, board):
    if start_pos[0] == end_pos[0]: # horizontal movement
        oriented_distance = end_pos[1]-start_pos[1]
        orientation = oriented_distance//abs(oriented_distance)
        for i in range(orientation, oriented_distance, orientation):
            if board[start_pos[0]][start_pos[1]+i] is not None:
                return False
    elif start_pos[1] == end_pos[1]: # vertical movement
        oriented_distance = end_pos[0]-start_pos[0]
        orientation = oriented_distance//abs(oriented_distance)
        for i in range(orientation, oriented_distance, orientation):
            if board[start_pos[0]+i][start_pos[1]] is not None:
                return False
    else:
        return False
    return True
        

class ChessPiece:
    def __init__(self, color) -> None:
        self.name = ""
        self.color = color

    def is_valid_move(self, start_pos, end_pos, board, castles_allowed, player_turn, prev_move, end_piece):
        return False

    def get_all_valid_moves(self, pos, board, castles_allowed, player_turn, prev_move):
        moves = []
        
        for x in range(len(board)):
            for y, end_piece in enumerate(board[x]):
                if end_piece is not None and end_piece.color == self.color:
                    continue
                if isinstance(self, PawnPiece) and x == 3.5-3.5*self.color:
                    continue
                
                if self.is_valid_move(pos, [x, y], board, castles_allowed, player_turn, prev_move, end_piece):
                    conversion = isinstance(self, PawnPiece) and x == 3.5+player_turn*3.5
                    
                    if not conversion:
                        moves.append([pos, [x, y], None])
                    else:
                        moves.append([pos, [x, y], "q"])
                        moves.append([pos, [x, y], "r"])
                        moves.append([pos, [x, y], "b"])
                        moves.append([pos, [x, y], "n"])

        return moves

class KingPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = KING

    def is_valid_move(self, start_pos, end_pos, board, castles_allowed, player_turn, *args, **kwargs):
        if abs(end_pos[1]-start_pos[1]) == 2 and end_pos[0] == start_pos[0]: # castle
            if end_pos[1] > start_pos[1]: # king side castle
                if (
                board[start_pos[0]][start_pos[1]+1] is None and
                board[start_pos[0]][start_pos[1]+2] is None
                ):
                    return castles_allowed[-player_turn+2]
            else: # queen side castle
                if (
                board[start_pos[0]][start_pos[1]-1] is None and
                board[start_pos[0]][start_pos[1]-2] is None and
                board[start_pos[0]][start_pos[1]-3] is None
                ):
                    return castles_allowed[-player_turn+1]
        
        return (
            abs(end_pos[0]-start_pos[0]) == 1 and abs(end_pos[1]-start_pos[1]) <= 1 or 
            abs(end_pos[1]-start_pos[1]) == 1 and abs(end_pos[0]-start_pos[0]) <= 1
        )

class QueenPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = QUEEN
        
    def is_valid_move(self, start_pos, end_pos, board, *args, **kwargs):
        return validate_bishop_move(start_pos, end_pos, board) or validate_rook_move(start_pos, end_pos, board)
    
class RookPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = ROOK

    def is_valid_move(self, start_pos, end_pos, board, *args, **kwargs):
        return validate_rook_move(start_pos, end_pos, board)
    
class BishopPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = BISHOP

    def is_valid_move(self, start_pos, end_pos, board, *args, **kwargs):
        return validate_bishop_move(start_pos, end_pos, board)
    
class KnightPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = KNIGHT

    def is_valid_move(self, start_pos, end_pos, *args, **kwargs):
        return (
            abs(end_pos[0]-start_pos[0]) == 2 and abs(end_pos[1]-start_pos[1]) == 1 or
            abs(end_pos[1]-start_pos[1]) == 2 and abs(end_pos[0]-start_pos[0]) == 1
        )
    
class PawnPiece(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.name = PAWN

    def is_valid_move(self, start_pos, end_pos, board, _, player_turn, prev_move, end_piece):
        # En Passant
        if (
            prev_move is not None and
            prev_move[3] and
            prev_move[1][0] == start_pos[0] and
            (prev_move[1][0]+prev_move[0][0])//2 == end_pos[0] and
            abs(start_pos[1]-prev_move[1][1]) == 1 and
            end_pos[1] == prev_move[1][1]
        ):
            return True
        
        # Forward Move
        if end_pos[1] == start_pos[1] and end_pos[0]-start_pos[0] == player_turn and end_piece is None:
            return True
        
        # Capture Move
        if (
            end_piece is not None and
            end_piece.color != player_turn and
            abs(end_pos[1]-start_pos[1]) == 1 and
            end_pos[0]-start_pos[0] == player_turn
        ):
            return True
        
        # Initial Move
        init_row = 1 if player_turn == 1 else 6
        if (
            end_piece is None and
            board[end_pos[0]-player_turn][end_pos[1]] is None and
            start_pos[0] == init_row and end_pos[1] == start_pos[1] and
            end_pos[0]-start_pos[0] == 2*player_turn
        ):
            return True
        
        return False