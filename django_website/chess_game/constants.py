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

NUM_TO_REPRESENTATION = {
    -6: KING,
    -5: QUEEN,
    -4: ROOK,
    -3: BISHOP,
    -2: KNIGHT,
    -1: PAWN,
    0: ".",
    1: PAWN.upper(),
    2: KNIGHT.upper(),
    3: BISHOP.upper(),
    4: ROOK.upper(),
    5: QUEEN.upper(),
    6: KING.upper(),
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
ENCRYPTION_KEY = "SHr)FG4*(JKL$q12_MNDweYz,.VC-BXt'3Apoiu"