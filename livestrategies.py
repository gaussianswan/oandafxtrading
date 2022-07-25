from sqlite3 import Date
import numpy as np 
import pandas as pd 
import tpqoa

from collections import defaultdict

class OANDALiveStrategy(tpqoa.tpqoa): 

    def __init__(self, instrument: str, granularity: pd.Timedelta, trade_size: int, conf_file: str = 'oanda.cfg', timezone = 'US/Eastern'):
        super().__init__(conf_file)

        self._instrument = instrument
        self._granularity = granularity
        self._trade_size = trade_size
        self._conf_file = conf_file
        self._timezone = timezone

        self._historical_data = pd.DataFrame()
        self._historical_ohlc = pd.DataFrame()
        self._net_positions = defaultdict(float)

        self._num_ticks = 0
        self._current_state = 0
        self._most_recent_bar = None

    def get_historical_data(self): 
        return self._historical_data

    def get_historical_ohlc(self): 
        return self._historical_ohlc

    def update_historical_data(self, df: pd.DataFrame): 
        self._historical_data = pd.concat([self._historical_data, df])

    def update_historical_ohlc(self): 
        self._historical_ohlc = self.create_ohlc(self._historical_data, frequency=self._granularity)
        self._most_recent_bar = self._historical_ohlc.iloc[-1]

    def update_net_positions(self): 
        positions = self.get_positions()
        if len(positions) != 0:  
            for position in positions: 
                instrument = position['instrument']
                long_units = float(position['long']['units'])
                short_units = float(position['short']['units'])
                net_units = long_units - short_units
                self._net_positions[instrument] = net_units

    def get_net_positions(self): 
        return self._net_positions

    def close_out(self) -> None: 
        """Closes out any positions that we have live

        Returns:
            _type_: _description_
        """
        self.update_net_positions()
        self.create_order(instrument=self._instrument, units = -self._net_positions[self._instrument])

        print("All positions closed out!")

        self._num_ticks = 0
        self._current_state = 0
    
    @staticmethod 
    def create_ohlc(df: pd.DataFrame, frequency: str, col: str = 'Mid'): 

        resampled = df.resample(rule = frequency)

        o = resampled.first()
        h = resampled.max()
        l = resampled.min()
        c = resampled.last()

        df = pd.concat([o[col], h[col], l[col], c[col]], axis = 1)
        df.columns = ['Open', 'High', 'Low', 'Close']
        df.fillna(method = 'ffill', inplace=True)
        return df

class OANDASMALiveStrategy(OANDALiveStrategy): 

    def __init__(self, instrument: str, short_period: int, long_period: int, granularity: pd.Timedelta, trade_size: int, long_short = True, conf_file: str = 'oanda.cfg', timezone = 'US/Eastern'): 
        """Constructor for the OANDA Simple Moving Average Strategy

        Args:
            instrument (str): Instrument that you'd like to trade on OANDA. Must be a valid instrument in the system
            short_period (int): Short period for the simple moving average
            long_period (int): Long period for the simple moving average
            granularity (str): Granularity for the time series data to trade on. 
            trade_size (int): Size of the trade in units that we are going to do every time. 
            long_short (bool, optional): _description_. Defaults to True.
            config_file (str, optional): _description_. Defaults to 'oanda.cfg'.
        """
        super().__init__(instrument=instrument, granularity=granularity, trade_size=trade_size, conf_file=conf_file, timezone=timezone)

        assert short_period < long_period, "You can't create a strategy that has a short period longer than your long period."
        self._short_period = short_period
        self._long_period = long_period
        self._long_short = long_short
        self._short_period_col_name = f"SMA_{short_period}"
        self._long_period_col_name = f"SMA_{long_period}"

    def on_success(self, time, bid, ask): 

        # On each message, we are going to do the following
        # 1. Update our dataset with the most recent tick information (bid and ask) 
        # 2. Check our position state
        # 3. Read our historical information and see if we should make an order

        # Updating historical information
        self._num_ticks += 1
        if (self._num_ticks % 20 == 0): 
            print(self._num_ticks)
            
        bid_ask_spread = (ask - bid)
        mid = bid + (bid_ask_spread/2)
        tick_timestamp = pd.Timestamp(time, tz = self._timezone)

        df = pd.DataFrame([[time, bid, ask, mid, bid_ask_spread]], columns = ['Time', 'Bid', 'Ask', 'Mid', 'Spread'])
        df.set_index('Time', inplace = True)
        df.index = pd.to_datetime(df.index)
        
        self.update_historical_data(df)
        self.update_net_positions()

        # We have to make sure that we are always net long or short
        if self._current_state == 0: 
            order_size = self._trade_size
        else: 
            order_size = 2 * self._trade_size

        # If a sufficient amount of time has passed since last tick and the last bar we saw
        # we update the historical ohlc, update our signals, and then see if there is a trade to be done
        if self._most_recent_bar is not None: 
            latest_time = self._most_recent_bar.name.tz_convert(self._timezone)
            if tick_timestamp > latest_time + self._granularity: 
                self.update_historical_ohlc()
                if self._historical_ohlc.shape[0] > self._long_period:
                    self.update_signal()
                    self.execute_on_signal(order_size=order_size)
        else: 

            # We have to update the OHLC at least once at the start
            self.update_historical_ohlc()


    def run(self, **kwargs): 
        self._num_ticks = 0
        self._current_state = 0
        self.stream_data(instrument=self._instrument, **kwargs)

    def update_signal(self): 
        self._historical_ohlc[self._long_period_col_name] = self._historical_ohlc['Close'].rolling(self._long_period).mean()
        self._historical_ohlc[self._short_period_col_name] = self._historical_ohlc['Close'].rolling(self._short_period).mean()

    def execute_on_signal(self, order_size: int): 
        current_long_sma = self._historical_ohlc[self._long_period_col_name].iloc[-1]
        current_short_sma = self._historical_ohlc[self._short_period_col_name].iloc[-1]

        if current_short_sma > current_long_sma: # buy signal
            if self._current_state in [-1, 0]: 
                order = self.create_order(instrument=self._instrument, units = order_size, ret=True)
                print("Going long {} at a price of {}".format(self._instrument, order['price'])) 

                self._current_state = 1

        elif current_short_sma < current_long_sma: 
            if self._current_state in [0, 1]: 
                order = self.create_order(instrument=self._instrument, units = order_size, ret=True)
                print("Going short {} at a price of {}".format(self._instrument, order['price']))

                self._current_state = -1

    
        
    def __repr__(self) -> str: 

        return f"OANDASMALiveStrategy(instrument = '{self._instrument}', short_period = {self._short_period}, long_period = {self._long_period}, granularity = '{self._granularity}', long_short = {self._long_short}, config_file = '{self._config_file}')"

    def __str__(self) -> str: 

        description = """
        Live SMA Strategy on OANDA
        Instrument: {}
        Short Period: {}
        Long Period: {}
        Granularity: {}
        Long Short: {}
        OANDA Config File: {}
        """.format(self._instrument, self._short_period, self._long_period, self._granularity, self._long_short, self._config_file)

        return description

if __name__ == '__main__': 
    strat_params = {
    'instrument': 'EUR_USD', 
    'short_period': 20, 
    'long_period': 50, 
    'granularity': pd.Timedelta(seconds = 5), 
    'trade_size': 1000
    }

    strategy = OANDASMALiveStrategy(**strat_params)
    strategy.run(stop = 150)







