import logging
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.trend import ADXIndicator
from ta.trend import MACD


class YFinance:
    def __init__(self, ticker="^NSEI", period="1000d", interval="1d", data_location=None):
        self.data = None
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.file_name = data_location + ticker.upper() + ".csv"

        '''
        if ticker[0] == '^':
            self.file_name = data_location + ticker[1:].upper() + ".csv"
        else:
            self.file_name = data_location + ticker.upper() + ".csv"
        '''

    def fetch_data(self):
        if self.ticker == "SPY":
            self.data = yf.download(tickers=self.ticker, period=self.period, interval="1d", start="2019-01-01")
        else:
            self.data = yf.download(tickers=self.ticker, period=self.period, interval=self.interval, start="2019-01-01")
        return self.data

    def load_data(self):
        logging.info("Data Fetch Started")
        self.data = self.fetch_data()
        # print(self.data.head())
        logging.info("Data Fetch Completed")

        # Add RSI
        indicator_rsi = RSIIndicator(self.data['Close'], window=14)
        # Add ADX/DMI
        indicator_adx = ADXIndicator(self.data['High'], self.data['Low'], self.data['Close'], window=14)
        # Add SMA 20
        # indicator_sma = SMAIndicator(self.data['Close'], window=20)
        # indicator_sma2 = SMAIndicator(self.data['Close'], window=13)
        # Add EMA 20
        indicator_ema = EMAIndicator(self.data['Close'], window=21)
        indicator_ema2 = EMAIndicator(self.data['Close'], window=8)
        # add MACD
        indicator_macd = MACD(self.data['Close'])

        # Calculate RDX
        self.data['rdx'] = indicator_rsi.rsi() + indicator_adx.adx_pos() - indicator_adx.adx_neg()
        self.data['pdi'] = indicator_adx.adx_pos()
        self.data['mdi'] = indicator_adx.adx_neg()
        self.data['adx'] = indicator_adx.adx()
        self.data['rsi'] = indicator_rsi.rsi()
        # self.data['sma20'] = indicator_sma.sma_indicator()
        # self.data['sma13'] = indicator_sma2.sma_indicator()
        self.data['ema21'] = indicator_ema.ema_indicator()
        self.data['ema8'] = indicator_ema2.ema_indicator()
        self.data['macd_diff'] = indicator_macd.macd_diff()
        self.data['adx_diff'] = abs(abs((indicator_adx.adx_pos() - indicator_adx.adx_neg())).diff())
        self.data['spike_exists'] = self.data['adx_diff'].gt(30)
        self.data['spike14'] = self.data['spike_exists'].rolling(14).mean().gt(0)

        logging.info("Custom data added")

        self.data = self.data.round(decimals=2)
        self.data.to_csv(self.file_name)
        logging.info("data written to data.csv file")
        return self.data
