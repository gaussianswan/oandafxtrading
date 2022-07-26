import pandas as pd
from livestrategies import OANDASMALiveStrategy
from iofuncs import pickle_to_file

params = {
    'instrument': 'EUR_USD',
    'short_period': 10,
    'long_period': 30,
    'granularity': pd.Timedelta(seconds = 30),
    'trade_size': 100000,
    'long_short': True,
    'timeout': 21600
}

sma_strategy = OANDASMALiveStrategy(**params)
sma_strategy.run()
print("Starting Strategy Now")
filename = 'GBP_USD_s10_l30_30seconds.pkl'
pickle_to_file(sma_strategy, filename=filename)
