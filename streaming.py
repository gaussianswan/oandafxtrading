import datetime
import tpqoa
import pandas as pd 

class Streamer(tpqoa.tpqoa): 

    def __init__(self, config_file: str = 'oanda.cfg', timezone: str = 'US/Eastern'): 
        super().__init__(config_file)
        self._config_file = config_file
        self._timezone= timezone
        self._start_time = pd.Timestamp(datetime.datetime.now(), tz=timezone)

    def on_success(self, tick, bid, ask): 
        tick_timestamp = pd.Timestamp(tick, tz = self._timezone)
        time_diff = tick_timestamp - self._start_time

        print("About {} seconds have elapsed".format(time_diff.total_seconds()))

        