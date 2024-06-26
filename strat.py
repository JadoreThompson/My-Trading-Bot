import app
import pandas as pd


def get_trend(df, current_candle, back_candles):
    df = df.reset_index().copy()
    start = max(0, current_candle - back_candles)
    end = current_candle
    relevant_rows = df.iloc[start: end]

    if current_candle - 5 < 0 and current_candle >= len(df):
        return 'OoR'

