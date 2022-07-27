import pandas as pd
import numpy as np
from oandafxtrading.backtesting.historicaldata import OANDAHistoricalData

class OANDABacktestStrategy:

    def __init__(self, instrument: str, start_date: str, end_date: str, granularity: str, long_short = True):
        self._instrument = instrument
        self._start_date = start_date
        self._end_date = end_date
        self._granularity = granularity
        self._long_short = long_short
        self._historical_data = OANDAHistoricalData(instrument=instrument, start_date=start_date, end_date=end_date, granularity=granularity, price_type='M')

    def get_strategy_statistics(self, results: pd.DataFrame) -> dict:
        """Calculates strategy statistics and returns it as a dictionary

        Args:
            results (pd.DataFrame): Results of a backtest in a dataframe

        Returns:
            dict: _description_
        """

        total_return = np.exp(results['strategy_return'].sum()) - 1
        daily_volatility = results['strategy_return'].std()
        annualized_volatility = daily_volatility * np.sqrt(252)
        annualized_return = results['strategy_return'].mean() * 252
        sharpe = annualized_return / annualized_volatility

        summary = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_vol': annualized_volatility,
            'sharpe': sharpe
        }

        return summary


class OANDASMAStrategy(OANDABacktestStrategy):

    def __init__(self, instrument: str, short_period: int, long_period: int, start_date: str, end_date: str, granularity: str, long_short = True):

        super().__init__(instrument = instrument, start_date = start_date, end_date = end_date, granularity = granularity, long_short = long_short)
        assert short_period < long_period, "The short period has to be shorter in value than the long period";

        self._short_period = short_period;
        self._long_period = long_period;
        self._short_period_col_name = "SMA_{}".format(self._short_period)
        self._long_period_col_name = 'SMA_{}'.format(self._long_period)

    def run_strategy(self) -> pd.DataFrame:

        candles = self._historical_data.data.copy()
        candles['log_c'] = candles['c'].apply(np.log)
        candles['log_c_returns'] = candles['log_c'].diff().dropna()

        candles[self._short_period_col_name] = candles['c'].rolling(self._short_period).mean()
        candles[self._long_period_col_name] = candles['c'].rolling(self._long_period).mean()
        candles.dropna(inplace = True)

        position = [] # Starting with a neutral position

        for i in range(candles.shape[0]):
            candle = candles.iloc[i]
            if candle[self._short_period_col_name] > candle[self._long_period_col_name]:
                position.append(1)

            elif candle[self._short_period_col_name] < candle[self._long_period_col_name]:

                if self._long_short:
                    position.append(-1)
                else:
                    position.append(0)

        candles['strategy_position'] = position
        candles['strategy_position'] = candles['strategy_position'].shift(1) ## Have to shift back one since we are going long at the close of the previous day
        candles.dropna(inplace=True)

        candles['strategy_return'] = candles['strategy_position'] * candles['log_c_returns']
        candles['strategy_cumulative_return'] = 1 + candles['strategy_return'].cumsum();

        return_cols = ['c', 'log_c', 'log_c_returns', self._short_period_col_name, self._long_period_col_name, 'strategy_position', 'strategy_return', 'strategy_cumulative_return']
        return (self.get_strategy_statistics(candles), candles[return_cols])

class OANDAEMAStrategy(OANDABacktestStrategy):

    def __init__(self, instrument: str, short_halflife: float, long_halflife: float, start_date: str, end_date: str, granularity: str, long_short=True):
        super().__init__(instrument, start_date, end_date, granularity, long_short)

        self._short_halflife = short_halflife
        self._long_halflife = long_halflife
        self._short_period_col_name = f'EMA_{self._short_halflife}'
        self._long_period_col_name = f'EMA_{self._long_halflife}'

    def run_strategy(self):
        candles = self._historical_data.data.copy()
        candles['log_c'] = candles['c'].apply(np.log)
        candles['log_c_returns'] = candles['log_c'].diff().dropna()

        candles[self._short_period_col_name] = candles['c'].ewm(halflife = self._short_halflife).mean()
        candles[self._long_period_col_name] = candles['c'].ewm(halflife = self._long_halflife).mean()
        candles.dropna(inplace = True)

        position = [] # Starting with a neutral position

        for i in range(candles.shape[0]):
            candle = candles.iloc[i]
            if candle[self._short_period_col_name] > candle[self._long_period_col_name]:
                position.append(1)

            elif candle[self._short_period_col_name] < candle[self._long_period_col_name]:

                if self._long_short:
                    position.append(-1)
                else:
                    position.append(0)

        candles['strategy_position'] = position
        candles['strategy_position'] = candles['strategy_position'].shift(1) ## Have to shift back one since we are going long at the close of the previous day
        candles.dropna(inplace=True)

        candles['strategy_return'] = candles['strategy_position'] * candles['log_c_returns']
        candles['strategy_cumulative_return'] = 1 + candles['strategy_return'].cumsum();

        return_cols = ['c', 'log_c', 'log_c_returns', self._short_period_col_name, self._long_period_col_name, 'strategy_position', 'strategy_return', 'strategy_cumulative_return']
        return (self.get_strategy_statistics(candles), candles[return_cols])

    def __repr__(self) -> str:

        representation = "OANDAEMAStrategy(instrument = '{}', short_halflife = {}, long_halflife = {}, start_date = '{}', end_date = '{}', granularity = '{}', long_short = {}".format(
            self._instrument,
            self._short_halflife,
            self._long_halflife,
            self._start_date,
            self._end_date,
            self._granularity,
            self._long_short
        )

        return representation


    def __str__(self) -> str:

        representation = f"""
        EMA Strategy for {self._instrument} from {self._start_date} to {self._end_date} using a granuarlity of {self._granularity}
        """

        return representation


class OANDASMAEMAStrategy(OANDABacktestStrategy):
    """Strategy where look the crossover between an EMA line and an SMA line. If the EMA line is above the
    SMA line, then we are going to be long. If the other, we are short.
    """

    def __init__(self, instrument: str, ema_period: int, sma_period: int, start_date: str, end_date: str, granularity = 'D', long_short = True) -> None:
        super().__init__(instrument, start_date, end_date, granularity, long_short)
        self._instrument = instrument
        self._ema_period = ema_period
        self._sma_period = sma_period
        self._ema_col_name = f'EMA_{self._ema_period}'
        self._sma_col_name = f'SMA_{self._sma_period}'

    def run_strategy(self):
        candles = self._historical_data.data.copy()
        candles['log_c'] = candles['c'].apply(np.log)
        candles['log_c_returns'] = candles['log_c'].diff().dropna()

        candles[self._ema_col_name] = candles['c'].ewm(halflife = self._ema_period).mean()
        candles[self._sma_col_name] = candles['c'].rolling(self._sma_period).mean()
        candles.dropna(inplace = True)

        position = [] # Starting with a neutral position

        for i in range(candles.shape[0]):
            candle = candles.iloc[i]
            if candle[self._ema_col_name] > candle[self._sma_col_name]:
                position.append(1)

            elif candle[self._ema_col_name] < candle[self._sma_col_name]:

                if self._long_short:
                    position.append(-1)
                else:
                    position.append(0)

        candles['strategy_position'] = position
        candles['strategy_position'] = candles['strategy_position'].shift(1) ## Have to shift back one since we are going long at the close of the previous day
        candles.dropna(inplace=True)

        candles['strategy_return'] = candles['strategy_position'] * candles['log_c_returns']
        candles['strategy_cumulative_return'] = 1 + candles['strategy_return'].cumsum();

        return_cols = ['c', 'log_c', 'log_c_returns', self._ema_col_name, self._sma_col_name, 'strategy_position', 'strategy_return', 'strategy_cumulative_return']
        return (self.get_strategy_statistics(candles), candles[return_cols])




