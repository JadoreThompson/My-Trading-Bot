import pandas as pd
from tqdm import tqdm

import asyncio

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

import numpy as np

df = pd.read_csv('BINANCE_BTCUSDT, 1.csv')
tqdm.pandas()


def trend_detection(df, current_candle, back_candles):
    df = df.reset_index().copy()
    start = max(0, current_candle - back_candles)
    end = current_candle
    position = current_candle - back_candles
    relevant_rows = df.iloc[start: end]

    if (current_candle - back_candles) < 0 or current_candle >= len(df):
        return 'Out of Range'

    if relevant_rows['close'][position] > relevant_rows['open'][position]:
        if (relevant_rows['close'][position + 1] > relevant_rows['open'][position + 1]) and (
                relevant_rows['close'][position + 1] > relevant_rows['high'][position]):
            return 0

    elif relevant_rows['close'][position] < relevant_rows['open'][position]:
        if (relevant_rows['close'][position + 1] < relevant_rows['open'][position + 1]) and (
                relevant_rows['close'][position + 1] < relevant_rows['low'][position]):
            return 1


def signal_detection(df, current_candle, back_candles):
    df = df.reset_index().copy()
    start = max(0, current_candle - back_candles)
    end = current_candle
    relevant_rows = df.iloc[start: end]

    def check_up(row):
        if row['open'] < row['close']:
            return 1

    def check_down(row):
        if row['open'] < row['close']:
            return 0

    if trend_detection(df, current_candle, back_candles) == 1:
        relevant_rows = relevant_rows[current_candle-2:]
        signal = relevant_rows.apply(check_up, axis=1)

        return 1

    elif trend_detection(df, current_candle, back_candles) == 0:
        relevant_rows = relevant_rows[current_candle - 2:]
        signal = relevant_rows.apply(check_up, axis=1)

        return 0


def SIGNAL():
    return df.signal


def pointpos(x):
    if x['signal'] == 1.0:
        return x['low'] - 1e-3
    elif x['signal'] == 0.0:
        return x['high'] + 1e-3
    else:
        return np.nan


back_candles = 6

df['trend'] = df.progress_apply(lambda row: trend_detection(df, row.name, back_candles), axis=1)
df['signal'] = df.progress_apply(lambda row: signal_detection(df, row.name, back_candles), axis=1)
df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)


async def plot_chart(df):
    df = df.reset_index().copy()
    df = df[1:]

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        close=df['high'],
        high=df['high'],
        low=df['low']),
        go.Scatter(x=df.index, y=df['pointpos'], mode='markers', marker=dict(color='MediumPurple', size=5),
                   name='entry')
    ])

    return fig


async def main():
    fig = await plot_chart(df)
    fig.show()


if __name__ == '__main__':
    asyncio.run(main())
