import numpy as np
import tensorflow as tf
import pandas as pd


def makeSets(data, lookback_len):
    print("Normalizing...")
    dataX = data.iloc[:, 0:-1]
    dataX = normalizeMinMax(dataX)
    dataY = data.iloc[:, -1]
    dataY = normalizeMinMaxSplitZero(dataY)

    print("Preparing i/o data...")
    dataXArr = dataX.values.tolist()
    x_train = [
        [dataXArr[i - j] for j in range(lookback_len)]
        for i in range(lookback_len - 1, len(dataXArr))
    ]
    dataYArr = dataY.values.tolist()
    y_train = dataYArr[lookback_len - 1 :]

    return x_train, y_train


def toDataset(x, y):
    return tf.data.Dataset.from_tensor_slices((x, y))


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


def normalizeMinMax(data):
    return ((data - data.min()) / (data.max() - data.min())) * 2 - 1


def normalizeMinMaxSplitZero(data):
    max = data.max()
    min = data.min()
    newData = data.copy()
    newData[data > 0] = ((data[data > 0] - 0) / (max - 0)) * 2 - 1
    newData[data < 0] = ((data[data < 0] - min) / (0 - min)) * 2 - 1
    return newData
