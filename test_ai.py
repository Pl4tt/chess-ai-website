import tensorflow as tf
from tensorflow import keras

# player: 1=white, -1=black
board = [
    []
]

def ai_eval(position, player) -> int:
    pass

def possible_moves(position, player) -> list:
    pass

def move(position, move): # returns new position after move
    pass

def best_move(position, player, depth):
    if depth == -1:
        return position, None, ai_eval(position, player)

    best_position = None
    best_move = None
    best_eval = -float("inf")
    
    for pmove in possible_moves(position, player):
        new_position = move(position, pmove)
        curr_position, curr_move, curr_eval = best_move(new_position, -player, depth-1)
        
        if curr_move is None:
            curr_move = pmove

        if player*curr_eval > best_eval:
            best_position = curr_position
            best_move = pmove
            best_eval = player*curr_eval

    return best_position, best_move, best_eval




