import logging

import pandas as pd
import yFin


class RankData:
    def __init__(self):
        self.symbols = None
        self.data_location = "./stock_data/"
        self.data_interval = "1d"
        self.rank_location = "./rank_data/"

    def load_data(self, target_symbols="US200.csv"):
        df = pd.read_csv(target_symbols)
        self.symbols = df['SYMBOL']
        print(type(self.symbols))
        i = 0

        try:
            for stock in self.symbols[i:]:
                yf = yFin.YFinance(ticker=stock, data_location=self.data_location)
                # print(yf.tail(1))
                df = yf.load_data()
                print(df.tail(1))

        except ValueError as value:
            print("value error: ", value)
        except Exception as ex:
            print("Exception occurred.")

    def rank_data(self, target_symbols="US200.csv"):
        df = pd.read_csv(target_symbols)
        self.symbols = df['SYMBOL']
        i = 0

        try:
            start = 251
            end = 1020

            for start in range(start, end):
                rows_list = []
                i = 0

                for stock in self.symbols[i:]:
                    # print(stock)
                    df = pd.read_csv(self.data_location+stock+".csv")
                    # print(df)
                    d = df.iloc[start].Date[:10]
                    # print(d)
                    d1 = str(d).replace("-", "")
                    # print(stock)
                    # print(type(df.iloc[251].Date))
                    dict1 = {}
                    dict1.update(df.iloc[start])
                    # print(df.iloc[start])
                    rows_list.append(dict1)
                    # print("done with: ", stock)

                df = pd.DataFrame(rows_list, columns=['Close', 'rdx', 'sma20', 'ema21', 'sma13', 'ema13'])
                # print(df.tail(1))
                df['Ticker'] = self.symbols
                # print(df.tail(1))
                df = df[['Ticker', 'Close', 'rdx', 'sma20', 'ema21', 'sma13', 'ema13']]
                # print(df.tail(1))
                df = df.sort_values(by=['rdx'], ascending=False)
                # print(df.tail(1))
                df.to_csv(self.rank_location + "rank_data_" + d1 + ".csv", index=False)
                print("completed rank: ", start)
            # print(df)

        except ValueError as value:
            print("value error.")

        except Exception as ex:
            print("Exception occurred.", ex)


