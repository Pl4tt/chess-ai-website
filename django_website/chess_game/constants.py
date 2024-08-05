KING = "k"
QUEEN = "q"
ROOK = "r"
BISHOP = "b"
KNIGHT = "n"
PAWN = "p"

PIECE_TO_NUM = {
    PAWN: 1,
    KNIGHT: 2,
    BISHOP: 3,
    ROOK: 4,
    QUEEN: 5,
    KING: 6,
}
NUM_TO_PIECE = {
    1: PAWN,
    2: KNIGHT,
    3: BISHOP,
    4: ROOK,
    5: QUEEN,
    6: KING,
}

WHITE = "w"
BLACK = "b"

SQUARE_TO_COORDINATE = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8
}

ALLOWED_TYPES = ["multiplayer", "ai"]

ENCRYPTION_CHARS = "ai-1234567890multiplayer"
ENCRYPTION_KEY = "SHr)FG4°*ç(JKL$q§12='?^MNDweYz,.VC-;BXt:_3A>poiu<"