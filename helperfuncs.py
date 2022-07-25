from matplotlib import ticker
import pandas as pd

def create_ohlc_candles(tick_data: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """Creates OHLC candles using some frequency that you decide

    Args:
        tick_data (pd.DataFrame): datframe that has tick by tick data with time, bid, ask, and mid price
        frequency (str): Frequency that you'd like to aggregate to

    Returns:
        pd.DataFrame: _description_
    """ 
    #TODO - IMPLEMENT THIS FUNCTION
    pass 