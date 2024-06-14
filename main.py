import asyncio
import pandas as pd
import pandas_ta as ta

# Data Formatting
# try:
df = pd.read_csv("FX_EURUSD, 5.csv")
df = pd.DataFrame(df)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = df[df.high != df.low]
# print(df)
df = df.rename(columns={'close': 'Close', 'open': 'Open', 'high': 'High', 'low': 'Low'})
# print(df)
df.set_index('time')

df['EMA_slow'] = ta.ema(df.Close, length=50)
df['EMA_fast'] = ta.ema(df.Close, length=30)
boli_bands = ta.bbands(df.Close, length=20, std=2)
df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=7)
df = df.join(boli_bands)

pd.set_option('display.max_columns', 30)


def trend_direction(df, current_candle, back_candles):
    df_slice = df.reset_index().copy()  # resetting the index for getting the most recent rows
    start = max(0, current_candle - back_candles)  # the minimum can be 0 preventing accessing negative numbers
    end = current_candle  # stop looking at the last ( most recent ) candle
    relevant_rows = df_slice.iloc[start: end]

    if all(relevant_rows['EMA_fast'] > relevant_rows['EMA_slow']):
        return 2
    elif all(relevant_rows['EMA_fast'] > relevant_rows['EMA_slow']):
        return 1
    else:
        return 0


from tqdm import tqdm
tqdm.pandas()

df = df[-len(df): -1]
df.reset_index(inplace=True)
df['EMA_signal'] = df.progress_apply(lambda row: trend_direction(df, row.name, 6), axis=1)
df = df[df.EMA_signal != 0]


def total_signal(df, current_candle, back_candles):
    if (trend_direction(df, current_candle, back_candles) == 2 and df.Close[current_candle] < df['BBL_20_2.0'][current_candle]):
        return 2
    if (trend_direction(df, current_candle, back_candles) == 1 and df.Close[current_candle] > df['BBL_20_2.0'][current_candle]):
        return 1

    return 0


df['TOTAL_signal'] = df.progress_apply(lambda row: total_signal(df, row.name, 6), axis=1)
# df = df[df.TOTAL_signal != 0]


import numpy as np


def pointpos(x):
    if x['TOTAL_signal'] == 2:
        return x['Low'] - 1e-3
    elif x['TOTAL_signal'] == 1:
        return x['High'] + 1e-3
    else:
        return np.nan


df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)


# Plotting Graph
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import asyncio


async def plot_chart(df):
    dfpl = df.reset_index().copy()
    dfpl = dfpl[1:]

    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                         open=dfpl['Open'],
                                         close=dfpl['Close'],
                                         high=dfpl['High'],
                                         low=dfpl['Low']),
                          go.Scatter(x=dfpl.index, y=dfpl['EMA_slow'], line=dict(color='purple', width=1),
                                     name="EMA slow"),
                          go.Scatter(x=dfpl.index, y=dfpl['EMA_fast'], line=dict(color='orange', width=1),
                                     name="EMA fast"),
                          go.Scatter(x=dfpl.index, y=dfpl['BBU_20_2.0'], line=dict(color='blue', width=1), name='BBU'),
                          go.Scatter(x=dfpl.index, y=dfpl['BBL_20_2.0'], line=dict(color='blue', width=1), name='BBL')
                          ])
    # fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode='markers', marker=dict(color='MediumPurple', size=5),
    #                 name='entry')

    return fig


# Backtesting the strategy
from backtesting import Strategy
from backtesting import Backtest


def SIGNAL():
    return df.TOTAL_signal


class MyStrat(Strategy):
    mysize = 3000
    slcoef = 1.1
    TPSLRatio = 2

    # rsi_length = 16

    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        # df['RSI']=ta.rsi(df.Close, length=self.rsi_length)

    def next(self):
        super().next()
        slatr = self.slcoef * self.data.ATR[-1]
        TPSLRatio = self.TPSLRatio

        # if len(self.trades)>0:
        #     if self.trades[-1].is_long and self.data.RSI[-1]>=90:
        #         self.trades[-1].close()
        #     elif self.trades[-1].is_short and self.data.RSI[-1]<=10:
        #         self.trades[-1].close()

        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr * TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr * TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


bt = Backtest(df, MyStrat, cash=250, margin=1/100)
print(bt.run())


async def main():
    fig = await plot_chart(df)
    fig.show()


if __name__ == '__main__':
    asyncio.run(main())
