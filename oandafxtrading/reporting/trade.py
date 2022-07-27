class OANDATrade: 

    def __init__(self, side: str, entry_price: float, size: float, entry_date: str, instrument: str, trade_id: int, strategy_name: str = "Generic") -> None:
        self._side = side
        self._entry_price = entry_price
        self._size = size
        self._entry_date = entry_date
        self._instrument = instrument
        self._trade_id = trade_id
        self._strategy_name = strategy_name

        self._exit_price = None 
        self._exit_date = None 
        self._orders = []

    def is_closed(self): 
        return self._exit_price is not None

    def close_trade(self, exit_price, exit_date): 

        self._exit_price = exit_price
        self._exit_date = exit_date

    def __repr__(self) -> str:
        return "OANDATrade(side = '{}', entry_price = {}, size = {}, entry_date = '{}', instrument = '{}', trade_id = {}, strategy_name = '{}'".format(
            self._side, 
            self._entry_price, 
            self._size, 
            self._entry_date, 
            self._instrument, 
            self._trade_id,
            self._strategy_name
        )

    def __str__(self) -> str: 

        if not self.is_closed(): 
            representation = f"{self._side} {self._size} units of {self._instrument} at a price of {self._entry_price} at {self._start_date}"
        else: 
            representation = f"{self.side} {self.size} units of {self._instrument} at a price of {self._entry_price} at {self._entry_date} and closed out at exit price of {self._exit_price} at {self._exit_date}"

        return representation

        