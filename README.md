# OANDA FX Trading
Personal repository for testing out and implementing strategies on OANDA. This work is extendable to other types of securities that might be traded. However, I plan to use OANDA to start. Please do not take any of the materials and thoughts in here as any type of financial advice. I'm just trying to play around with code. Use any code here at your own risk!

The materials in here are inspired by the course on Udemy about Algorithmic Trading. You can find it [here](https://www.udemy.com/course/algorithmic-trading-with-python-and-machine-learning/). 

## Instructions in setting up environment
```bash
conda create -n fxtrading python=3.9
```
It's very important that we have the tpqoa package which is a client created by The Python Quants for OANDA trading
```bash
pip install git+https://github.com/yhilpisch/tpqoa
```

After you've set that up, try running this script to make sure things are working
```python
import tpqoa 

# Assumes you have a file in your directory called "oanda.cfg"
api = tpqoa.tpqoa('oanda.cfg')
api.get_instruments() # Returns all the tradeable instruments on OANDA
```

### Requirements

You need to set up an "oanda.cfg" file in the directory of this project so that it can be read.
In the oanda.cfg file you specify the account_id and account_token which you can get from the OANDA site. 
