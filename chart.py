import asyncio
import numpy as np

import plotly.graph_objects as go

from main import df


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


def pointpos(x):
    if x['signal'] == 1.0:
        return x['low'] - 1e-3
    elif x['signal'] == 0.0:
        return x['high'] + 1e-3
    else:
        return np.nan


df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)


async def main():
    fig = await plot_chart(df)
    fig.show()


if __name__ == '__main__':
    asyncio.run(main())
