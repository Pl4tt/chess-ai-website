import os
import json
import chess
import random
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers

# white = 1, black = -1

# board: [square0 (a8), square1 (a7), ..., square63 (h1), player, castleK, castleQ, castlek, castleq, enPassant]
# player: 1 / -1
# castle: 0/1
# enPassant: -1 / 0, 1, ..., 63 (- -> -1, a1 -> 0, a2 -> 1, ..., h8 -> 63)

piece_mappings = {
    "P": 1,
    "N": 2,
    "B": 3,
    "R": 4,
    "Q": 5,
    "K": 6,
    "p": -1,
    "n": -2,
    "b": -3,
    "r": -4,
    "q": -5,
    "k": -6,
}
board_mappings = {
    "a": 0,
    "b": 8,
    "c": 16,
    "d": 24,
    "e": 32,
    "f": 40,
    "g": 48,
    "h": 56
}

# dir_path = os.getcwd()

# # def get_datasets():
# #     train_cats = np.array([cv2.resize(cv2.imread(f"{dir_path}\\dataset\\training_set\\cats\\cat.{i}.jpg"), (128, 128)) for i in range(1, 4001)])  # (4000, 128, 128, 3)
# #     train_dogs = np.array([cv2.resize(cv2.imread(f"{dir_path}\\dataset\\training_set\\dogs\\dog.{i}.jpg"), (128, 128)) for i in range(1, 4001)])  # (4000, 128, 128, 3)
# #     test_cats = np.array([cv2.resize(cv2.imread(f"{dir_path}\\dataset\\test_set\\cats\\cat.{i}.jpg"), (128, 128)) for i in range(4001, 5001)])  # (1000, 128, 128, 3)
# #     test_dogs = np.array([cv2.resize(cv2.imread(f"{dir_path}\\dataset\\test_set\\dogs\\dog.{i}.jpg"), (128, 128)) for i in range(4001, 5001)])  # (1000, 128, 128, 3)
    
# #     train_images = np.concatenate((train_cats, train_dogs))  # (8000, 128, 128, 3)
# #     train_labels = np.concatenate((np.zeros((4000,)), np.ones((4000,))))  # (8000,)

# #     test_images = np.concatenate((test_cats, test_dogs))  # (2000, 128, 128, 3)
# #     test_labels = np.concatenate((np.zeros((1000,)), np.ones((1000,))))  # (2000,)

# #     train_images, train_labels = shuffle(train_images, train_labels)
# #     test_images, test_labels = shuffle(test_images, test_labels)

# #     return train_images, train_labels, test_images, test_labels

def create_model(num_hneurons):
    model = keras.Sequential()
    num_hlayers = len(num_hneurons)
    input_shape = (70,)

    model.add(layers.Dense(num_hneurons[0], input_shape=input_shape))

    for i in range(1, num_hlayers):
        model.add(layers.Dense(num_hneurons[i], activation="relu"))
        
    model.add(layers.Dense(1, activation="linear"))

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    return model

# def random_board(max_depth=200):
#     board = chess.Board()
#     depth = random.randrange(0, max_depth)
    
#     for _ in range(depth):
#         all_moves = list(board.legal_moves)
#         random_move = random.choice(all_moves)
#         board.push(random_move)
#         if board.is_game_over():
#             break

#     return board

def fit_model(model, input_data, output_data):
    print(1.1)
    model.fit(input_data[10:], output_data[10:], epochs=10, batch_size=512)
    print(1.2)
    result = model.evaluate(input_data[0:10], output_data[0:10])
    print(1.3)
    print(f"result: {result}")

def save_model(model):
    model.save("model.h5")

def load_model():
    return keras.models.load_model("model.h5")

def process_data(json_data):
    clean_input = []
    clean_output = []

    for position in json_data["data"]:
        fen = position["fen"].split()
        player = 1 if fen[1] == "w" else -1  # 1 for white, -1 for black

        best_evaluation = -player*float("inf")  # initially worst evaluation for current player
        
        for line in position["evals"][0]["pvs"]:
            # if color*best_evaluation == float("inf"):
            #     continue

            cp = line.get("cp")
            mate = line.get("mate")

            if cp is None:
                if mate is not None and player*mate > 0:
                    best_evaluation = player*float("inf")
            elif player == 1 and cp > best_evaluation or player == -1 and best_evaluation > cp:
                best_evaluation = cp
        
        matrix_fen = []


        for square in fen[0].replace("/", ""):
            if square in piece_mappings.keys():
                matrix_fen.append(piece_mappings.get(square))
            else:
                matrix_fen += [0]*int(square)
        
        matrix_fen += [
            player,
            int("K" in fen[2]),
            int("Q" in fen[2]),
            int("k" in fen[2]),
            int("q" in fen[2]),
            -1 if fen[3] == "-" else board_mappings[fen[3][0]] + int(fen[3][1])-1,
        ]

        clean_input.append(matrix_fen)

        if best_evaluation == +float("inf"):
            clean_output.append(1000000)
        elif best_evaluation == -float("inf"):
            clean_output.append(-1000000)
        else:
            clean_output.append(best_evaluation)
    
    return clean_input, clean_output


if __name__ == "__main__":
    # model = create_model([1024, 256, 64])
    # model.summary()
    # print(random_board())

    # with open("lichess_db_eval.json", "r") as input_file:
    #     print(0)
    #     lines = input_file.read().splitlines()

    #     with open("usable_lichess_db_eval.json", "w") as output_file:
    #         print(1)
    #         for count, line in enumerate(lines):
    #             if count == 0:
    #                 output_file.write("{data: [" + line + ",\n")
    #             elif count == len(lines)-1:
    #                 output_file.write("]}")
    #             else:
    #                 output_file.write(line + ",\n")

    with open("test_eval.json") as json_file:
        json_data = json.load(json_file)
    
    input_data, output_data = process_data(json_data)
    print(input_data, output_data)
    
    model = create_model([512])
    print(0)
    fit_model(model, input_data, output_data)
    print(1)
    # model.summary()
