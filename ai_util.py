import numpy as np
import tensorflow as tf
import pandas as pd


def makeSets(data):
    print("Normalizing...")
    dataX = data.iloc[:, 0:-1]
    dataX = ((dataX - dataX.min()) / (dataX.max() - dataX.min())) * 2 - 1
    dataXArr = dataX.values.tolist()

    print("Preparing i/o data...")
    x_train = [[dataXArr[i - 1] + dataXArr[i]] for i in range(1, len(dataXArr))]
    y_train = data.iloc[:, -1].values.tolist()[1:]

    return x_train, y_train


def toDataset(x, y):
    return tf.data.Dataset.from_tensor_slices((x, y)).batch(2048)


def buydec(df):
    vals = []
    lookahead = 30
    for i in range(len(df)):
        curClose = df["Close"].iloc[i]
        curBBW = df["BBUpper"].iloc[i] - df["BBLower"].iloc[i]
        closeLookahead = df["Close"].iloc[i : i + lookahead]
        maxClose = max(closeLookahead)
        minClose = min(closeLookahead)
        potentialUp = (maxClose - curClose) / curBBW
        potentialDown = (curClose - minClose) / curBBW
        potentialSum = potentialUp - potentialDown
        vals.append(potentialSum)

    return np.array(vals)
