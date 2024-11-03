import os
import json
import random
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import matplotlib.pyplot as plt

# white = 1, black = -1

# board: [square0 (a8), square1 (b8), ..., square63 (h1), player, castleK, castleQ, castlek, castleq, enPassant]
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
BATCH_SIZE = 256
BUFFER_SIZE = 20000

def plot_values(epochs, acc):

    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.title('Training accuracy')
    plt.legend()

    plt.figure()

    plt.savefig('/content/drive/MyDrive/accuracy.png')

    plt.show()

def create_model(num_hneurons, model_optimizer):
    model = keras.Sequential()
    num_hlayers = len(num_hneurons)
    input_shape = (70,)

    model.add(layers.InputLayer(input_shape=input_shape))

    for i in range(1, num_hlayers):
        model.add(layers.Dense(num_hneurons[i], activation="relu"))

    model.add(layers.Dense(1, activation="linear"))

    model.compile(optimizer=model_optimizer, loss="mean_squared_error", metrics=["accuracy"])

    return model

@tf.function
def train_step(data):
    x, y = data

    with tf.GradientTape() as tape:
        y_pred = model(x, training=True)  # Forward pass
        loss = model.compute_loss(y=y, y_pred=y_pred)

    trainable_vars = model.trainable_variables
    gradients = tape.gradient(loss, trainable_vars)

    model.optimizer.apply_gradients(zip(gradients, trainable_vars))

    for metric in model.metrics:
        if metric.name == "loss":
            metric.update_state(loss)
        else:
            metric.update_state(y, y_pred)

    return {m.name: m.result() for m in model.metrics}

def train(dataset, epochs):
    for epoch in range(epochs):
        print(f"start Epoch {epoch}")
        start = time.time()

        for data_batch in dataset:
            train_step(data_batch)

        if (epoch+1)%10 == 0:
            checkpoint.save(file_prefix=checkpoint_prefix)

        print(model.evaluate(test_inp, test_outp))
        print(f"Epoch {epoch} finished in {time.time()-start}")

def fit_model(model, dataset):
    epochs = 200

    with tf.device('/device:GPU:0'):
        print(0)
        history = model.fit(dataset, epochs=epochs)
        # history = model.fit(dataset)
        # train(dataset, epochs)

    # result = model.evaluate(input_data[0:100], output_data[0:100])

    # print(f"result: {result}")
    print("Done")
    plot_values(epochs, history.history["accuracy"])

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
    dataset = tf.data.Dataset.from_tensor_slices((input_data, output_data)).batch(BATCH_SIZE)
    print(dataset)
    
    optimizer = keras.optimizers.Adam(1e-4)
    model = create_model([70, 128, 32], optimizer)
    
    print(0)
    fit_model(model, dataset)
    print(1)
    # model.summary()
