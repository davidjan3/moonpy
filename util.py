import pandas as pd
import pandas_ta as ta
from time import perf_counter


def crossover(series0, series1):
    return series0[-2] < series1[-2] and series0[-1] >= series1[-1]


def crossunder(series0, series1):
    return crossover(series1, series0)


def bbandsLMH(*args):
    bb = ta.bbands(*args)
    bb = bb.drop(bb.columns[[3, 4]], axis=1)
    return bb


def bbandsLH(*args):
    bb = ta.bbands(*args)
    bb = bb.drop(bb.columns[[1, 3, 4]], axis=1)
    return bb


def adx(*args):
    adx = ta.adx(*args)
    adx = adx.drop(adx.columns[[1, 2]], axis=1)
    return adx.squeeze()


def davg(close, low, high):
    range = high - low
    p = close - low
    return (p / range) * 2.0 - 1


def millify(df):
    df.Open *= 1 / 1000.0
    df.High *= 1 / 1000.0
    df.Low *= 1 / 1000.0
    df.Close *= 1 / 1000.0
    return df


class timer:
    t = 0

    def start():
        timer.t = perf_counter()

    def stop(str="Timer"):
        nt = perf_counter()
        d = nt - timer.t
        print(f"{str} took:\t{d}")
        return d
