from setuptools import setup, find_packages

setup(
    authoer = 'Stephon Henry-Rerrie',
    description = "A package for handling OANDA trading",
    name = 'oandafxtrading',
    version = '0.1.0',
    packages = find_packages(include=['oandafxtrading', 'oandafxtrading.*']),
    install_requires = ['telegram_send', 'tpqoa', 'pandas', 'numpy'],
    python_requires = ">=3.7"
)



