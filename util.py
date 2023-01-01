import pandas as pd
import pandas_ta as ta


def crossover(series0, series1):
    return series0[-2] < series1[-2] and series0[-1] >= series1[-1]


def crossunder(series0, series1):
    return crossover(series1, series0)


def bbands(*args):
    bb = ta.bbands(*args)
    bb = bb.drop(bb.columns[[3, 4]], axis=1)
    return bb
