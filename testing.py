from backtesting import Strategy, Backtest
from main import SIGNAL, df

import pandas as pd

df = df.rename(columns={'high': 'High', 'low': 'Low', 'open': 'Open', 'close': 'Close'})
df['time'] = pd.to_datetime(df['time'], unit='s')
df = df.set_index(['time'])


class MyStrat(Strategy):
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        if self.signal1[-1] == 1.0:
            sl1 = self.data.Close[-1] * 1.02
            tp1 = self.data.Close[-1] - (self.data.Close[-1] - sl1)
            self .sell(tp=tp1, sl=sl1)
        elif self.signal1[-1] == 0.0:
            sl1 = self.data.Open[-1] * 0.98
            tp1 = self.data.Open[-1] + (self.data.Open[-1] - sl1)
            self.buy(sl=sl1, tp=tp1)


df = df.iloc[1: 500]

bt = Backtest(df, MyStrat, cash=100000)
stats = bt.run()
print(stats)
