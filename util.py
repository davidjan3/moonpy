import pandas as pd

def crossover(series0, series1):
  return series0[-2] < series1[-2] and series0[-1] >= series1[-1]

def crossunder(series0, series1):
  return crossover(series1, series0)
