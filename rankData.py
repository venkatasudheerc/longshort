import pandas as pd
import yFin


class RankData:
    def __init__(self, target="US"):
        self.symbols = None
        self.data_interval = "1d"
        self.data_location = "./stock_data/"
        self.rank_location = "./rank_data/"
        self.indices = pd.Series(['SPY', '^NSEI'])
        if target == "US":
            self.target_symbols = "US200.csv"
        else:
            self.target_symbols = "NSE200.csv"
            self.data_location = "./istock_data/"
            self.rank_location = "./irank_data/"


    def load_data(self):
        indices = pd.Series(['SPY', '^NSEI'])
        # print(type(indices))
        df = pd.read_csv(self.target_symbols)
        self.symbols = df['SYMBOL']
        # print(len(self.symbols))
        # print((self.symbols.append(indices, ignore_index=True)))
        i = 0
        try:
            for stock in self.symbols.append(self.indices, ignore_index=True)[i:]:
                yf = yFin.YFinance(ticker=stock, data_location=self.data_location)
                # print(yf.tail(1))
                df = yf.load_data()
                # print(df.tail(1))
        except ValueError as value:
            print("value error: ", value)
        except ArithmeticError as ex:
            print("Exception : ArithmeticError occurred.")
        except Exception as ex:
            print("Exception occurred.")

    def rank_data(self):
        df = pd.read_csv(self.target_symbols)
        self.symbols = df['SYMBOL']
        try:
            start = 80
            end = 101

            while start < end:
                rows_list = []
                i = 0

                for stock in self.symbols[i:]:
                    # print(stock)
                    if stock in self.indices.values:
                        continue
                    df = pd.read_csv(self.data_location+stock+".csv")
                    # print(df)
                    if end == 101:
                        print("end calculated based on stock: ", stock)
                        end = len(df)
                    d = df.iloc[start].Date[:10]
                    # print(d)
                    d1 = str(d).replace("-", "")
                    # print(stock)
                    # print(type(df.iloc[251].Date))
                    '''
                    if start > 1000:
                        print("stock")
                        print(df.iloc[start])
                    '''
                    dict1 = {}
                    dict1.update(df.iloc[start])

                    rows_list.append(dict1)
                    # print("done with: ", stock)

                df = pd.DataFrame(rows_list, columns=['Open', 'Close', 'rdx', 'ema21', 'ema13', 'ema8', 'spike14'])
                # print(df.tail(1))
                df['Ticker'] = self.symbols
                # print(df.tail(1))
                df = df[['Ticker', 'Open', 'Close', 'rdx', 'ema21', 'ema13', 'ema8', 'spike14']]
                # print(df.tail(1))
                df = df.sort_values(by=['rdx'], ascending=False)
                # print(df.tail(1))
                df.to_csv(self.rank_location + "rank_data_" + d1 + ".csv", index=False)
                print("completed rank: ", start)
                start = start + 1
            # print(df)

        except ValueError as value:
            print("value error.")

        except Exception as ex:
            print("Exception occurred.", ex)


