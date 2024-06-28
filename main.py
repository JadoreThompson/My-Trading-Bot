import pandas as pd
from tqdm import tqdm


# df = pd.read_csv('BINANCE_BTCUSDT, 1.csv') # this is the original dataframe that worked

df = pd.read_csv('Bitcoin_BTCUSDT.csv')
df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M').astype('int64') // 10**9

tqdm.pandas()


def trend_detection(df, current_candle, back_candles):
    df = df.reset_index().copy()
    start = max(0, current_candle - back_candles)
    end = current_candle
    position = current_candle - back_candles
    relevant_rows = df.iloc[start: end]

    if (current_candle - back_candles) < 0 or current_candle >= len(df):
        return 'NaN'

    if relevant_rows['close'][position] > relevant_rows['open'][position]:
        if (relevant_rows['close'][position + 1] > relevant_rows['open'][position + 1]) and (
                relevant_rows['close'][position + 1] > relevant_rows['high'][position]):
            return 0

    elif relevant_rows['close'][position] < relevant_rows['open'][position]:
        if (relevant_rows['close'][position + 1] < relevant_rows['open'][position + 1]) and (
                relevant_rows['close'][position + 1] < relevant_rows['low'][position]):
            return 1

    return 'NaN'

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
        signal = relevant_rows.apply(check_down, axis=1)

        return 0




def SIGNAL():
    return df.signal


df = df.iloc[1:500]
back_candles = 6

df['trend'] = df.progress_apply(lambda row: trend_detection(df, row.name, back_candles), axis=1)
df['signal'] = df.progress_apply(lambda row: signal_detection(df, row.name, back_candles), axis=1)


print(df)