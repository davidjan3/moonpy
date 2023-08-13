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
    return tf.data.Dataset.from_tensor_slices((x, y)).batch(60)


def buydec(df):
    maxVal = max(df.values)
    minVal = min(df.values)
    curVal = df.values[int(len(df) / 2)]
    curRel = (curVal - minVal) / (maxVal - minVal)

    return curRel * 2 - 1
