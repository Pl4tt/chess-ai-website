from copy import deepcopy
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from .board import ChessBoard
from .constants import NUM_TO_REPRESENTATION


REPETITION_PENALTY = 4

class module(nn.Module):
    def __init__(self, hidden_size_in, hidden_size_out, dropout_rate=0.5):
        super().__init__()
        self.conv1 = nn.Conv2d(hidden_size_in, hidden_size_out, 3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(hidden_size_out, hidden_size_out, 3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(hidden_size_out)
        self.bn2 = nn.BatchNorm2d(hidden_size_out)
        self.activation1 = nn.LeakyReLU()
        self.activation2 = nn.LeakyReLU()
        self.dropout = nn.Dropout(dropout_rate)

        self.shortcut = nn.Sequential()
        if hidden_size_in != hidden_size_out:
            self.shortcut = nn.Sequential(
                nn.Conv2d(hidden_size_in, hidden_size_out, kernel_size=1, stride=1, bias=False),
                nn.BatchNorm2d(hidden_size_out),
                nn.LeakyReLU()
            )

    def forward(self, x):
        x_input = torch.clone(x)

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.activation1(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.activation2(x)
        x = self.dropout(x)

        x += self.shortcut(x_input)

        return x

class ChessNet(nn.Module):
    def __init__(self, hidden_layers=4, hidden_size=200, hidden_sizes=[256, 1024, 512, 128, 32, 32]):
        super().__init__()
        self.hidden_layers = hidden_layers
        self.input_layer = nn.Conv2d(6, 256, 3, stride=1, padding=1)
        self.module_list = nn.ModuleList([module(hidden_sizes[i], hidden_sizes[i+1], 0.5-0.075*i) for i in range(len(hidden_sizes)-1)])
        self.output_layer = nn.Conv2d(32, 2, 3, stride=1, padding=1)

    def forward(self, x):
        x = self.input_layer(x)
        x = F.relu(x)

        for i in range(self.hidden_layers):
            x = self.module_list[i](x)

        x = self.output_layer(x)

        return x


def check_mate_single(board: ChessBoard):
    legal_moves = list(board.get_all_legal_moves())

    for move in legal_moves:
        temp_test_board = deepcopy(board)
        move_made = temp_test_board.make_move(*move)
    
        if move_made[0] and abs(temp_test_board.check_game_over()) == 1:
            return move

    return None

def distribution_over_moves(vals):
    probs = np.array(vals)
    probs = np.exp(probs)
    probs = probs / probs.sum()
    probs = probs**3
    probs = probs / probs.sum()

    return probs


letter_2_num = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
num_2_letter = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

def create_rep_layer(board, piece_type):
    s = "\n".join(map(lambda row: " ".join(map(lambda piece: NUM_TO_REPRESENTATION[piece], row)), board)).replace("[", "").replace("]", "").replace(",", "")
    s = re.sub(f"[^{piece_type}{piece_type.upper()} \n]", ".", s)
    s = re.sub(f"{piece_type}", "-1", s)
    s = re.sub(f"{piece_type.upper()}", "1", s)
    s = re.sub(f"\.", "0", s)

    board_mat = []
    for row in s.split("\n"):
        row = row.split(" ")
        row = [int(x) for x in row]
        board_mat.append(row)

    return np.array(board_mat)

def board_2_rep(board):
    pieces = ["p", "r", "n", "b", "q", "k"]
    layers = []

    for piece in pieces:
        layers.append(create_rep_layer(board, piece))

    return np.stack(layers)

def predict(model, inputs):
    model.eval()
    return model(inputs)

def choose_move(model, board: ChessBoard, color):
    legal_moves = list(board.get_all_legal_moves())
    
    move = check_mate_single(board)
    if move is not None:
        return move

    inputs = torch.Tensor(board_2_rep(board.integer_board[::-1])).float()
    inputs *= color
    inputs = inputs.unsqueeze(0)
    move = predict(model, inputs).detach().cpu().numpy()[0]

    vals = []
    froms = ["".join(map(str, legal_move[0])) for legal_move in legal_moves]
    froms = np.unique(np.array(froms), axis=0)

    for from_ in froms:
        val = move[0,:,:][7-int(from_[0]), int(from_[1])]
        vals.append(val)

    probs = distribution_over_moves(vals)

    chosen_from = str(np.random.choice(froms, size=1, p=probs)[0])[:2]

    vals = []
    for legal_move in legal_moves:
        from_ = "".join(map(str, legal_move[0]))
        if from_ == chosen_from:
            to = legal_move[1]
            val = move[1,:,:][7-to[0], to[1]]
            
            # Apply penalty for repeated positions
            temp_test_board = deepcopy(board)
            temp_test_board.make_move(*legal_move)
            seen_pos_num = temp_test_board.seen_positions[hash(str(temp_test_board.board))]

            if seen_pos_num > 1:
                val -= REPETITION_PENALTY*(seen_pos_num-1.9)
            

            if hash(str([legal_move[0], legal_move[1]])) in board.previous_5_moves:
                val -= 0.1*REPETITION_PENALTY
            
            vals.append(val)
        else:
            vals.append(-float("inf"))

    probs = distribution_over_moves(vals)

    chosen_move_index = np.random.choice(len(legal_moves), size=1, p=probs)

    chosen_move = legal_moves[chosen_move_index[0]]

    return chosen_move
