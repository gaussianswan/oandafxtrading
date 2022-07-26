from livestrategies import OANDASMALiveStrategy
import pandas as pd

strategy_params = {
    'instrument': 'GBP_USD', 
    'short_period': 20, 
    'long_period': 60, 
    'granularity': pd.Timedelta(minutes = 1), 
    'trade_size': 10000
}
