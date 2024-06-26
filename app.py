import pandas as pd
import os

current_dir = os.path.dirname(__file__)
csv_path = os.path.join(current_dir, 'data', 'BINANCE_BTCUSDT, 1.csv')

df = pd.read_csv(csv_path)