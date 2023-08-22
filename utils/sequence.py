import numpy as np

from constants import SEQUENCE_LENGTH


def create_sequences(data):
    x, y = [], []

    for i in range(len(data) - SEQUENCE_LENGTH):
        x.append(data[i : i + SEQUENCE_LENGTH])
        y.append(data[i + SEQUENCE_LENGTH])

    return np.array(x)
