import pandas as pd 
import numpy as np 
import tpqoa

class OANDAAccount(tpqoa.tpqoa): 

    def __init__(self, conf_file: str = 'oanda.cfg', account_name: str = "Stephon Test Account"):
        super().__init__(conf_file)

        self._account_name = account_name
        
    def get_security_list(self): 
        pass 


    