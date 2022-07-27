import pandas as pd

class OANDATrade:

    def __init__(self, oanda_fill_dict: dict, timezone = 'UTC'):

        for key, value in oanda_fill_dict.items():
            setattr(self, f"{key}", value)

        self.time = pd.Timestamp(self.time, tz=timezone)
        self.units = float(self.units)
        self.price = float(self.price)
        self.pl = float(self.pl)