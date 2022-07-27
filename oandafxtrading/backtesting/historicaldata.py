import pandas as pd
import numpy as np
import tpqoa

class OANDAHistoricalData:

    def __init__(self, instrument: str, start_date: str, end_date: str, granularity: str, price_type = 'A', config_file_path: str = None) -> None:

        if config_file_path:
            self.__api = tpqoa.tpqoa(config_file_path)
        else:
            self.__api = tpqoa.tpqoa('oanda.cfg')

        self.instruments_mapping = dict(self.__api.get_instruments());
        self._allowable_instruments = tuple(self.instruments_mapping.values());

        assert instrument in self._allowable_instruments, ''

        self._instrument = instrument;
        self._start_date = start_date;
        self._end_date = end_date;
        self._granularity = granularity;
        self._price_type = price_type
        self.data = self.get_data();

    def get_data(self):
        data = self.__api.get_history(
            instrument=self._instrument,
            start = self._start_date,
            end = self._end_date,
            granularity= self._granularity,
            price = self._price_type
        )

        return data

    def __repr__(self):

        return "OANDAHistoricalData(instrument = '{}', start_date = '{}', end_date = '{}', granularity = '{}')".format(self._instrument, self._start_date, self._end_date, self._granularity);

    def __str__(self):

        return "Historical OANDA pricing data for {} from {} to {} with a granularity of {}".format(self._instrument, self._start_date, self._end_date, self._granularity)




