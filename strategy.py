import glob
import os.path

import pandas as pd


class Strategy:
    def __init__(self, target="US"):
        self.rank_data_location = "./rank_data/"
        self.stock_data_location = "./stock_data/"
        self.portfolio = pd.DataFrame()
        self.short_portfolio = pd.DataFrame()
        self.closed_pos = pd.DataFrame()
        self.long_short_df = pd.DataFrame()
        self.cnt_max_open_pos = 0
        self.is_long_only = True
        self.index_df = pd.DataFrame()

        if target == 'US':
            self.index_file_name = self.stock_data_location + "SPY" + ".csv"
        else:
            self.rank_data_location = "./irank_data/"
            self.stock_data_location = "./istock_data/"
            self.index_file_name = self.stock_data_location + "^NSEI" + ".csv"

    def load_index(self):
        df = pd.read_csv(self.index_file_name)
        self.index_df = pd.DataFrame(columns=['Date', 'signal'])

        # Start with a long signal
        signal = "LONG"
        row_list = []
        for index, row in df.iterrows():
            dict1 = {}

            if row.ema8 > row.ema13 and row.rdx > 50:
                signal = "LONG"
            elif row.ema8 < row.ema13 and row.rdx < 50:
                signal = "SHORT"

            dict1.update({
                'Date': str(row.Date[:10]).replace("-", ""),
                'signal': signal
            })
            row_list.append(dict1)

        self.index_df = pd.DataFrame(row_list)
        self.index_df.to_csv("signal.csv", index=False)

    def load_index1(self):
        df = pd.read_csv(self.index_file_name)
        self.index_df = pd.DataFrame(columns=['Datetime', 'signal'])

        # Start with a long signal
        signal = "LONG"
        row_list = []
        for index, row in df.iterrows():
            if "15:30:00" not in row.Datetime:
                continue

            dict1 = {}
            if row.ema8 > row.ema13 and row.rdx > 50:
                signal = "LONG"
            elif row.ema8 < row.ema13 and row.rdx < 50:
                signal = "SHORT"

            dict1.update({
                'Date': str(row.Datetime[:10]).replace("-", ""),
                'signal': signal
            })
            row_list.append(dict1)

        self.index_df = pd.DataFrame(row_list)
        self.index_df.to_csv("signal.csv", index=False)

    def check_for_sl(self, df, d):
        temp = self.portfolio
        rows_list = []
        # print("Checking SL for ", d)
        for index, row in self.portfolio.iterrows():
            # print(index, " : ", row.Ticker)
            dict1 = {}
            if row.Ticker in df.values:
                df_row = df[df['Ticker'] == row.Ticker]
                if row.Signal == "Long":
                    if df_row.iloc[0]['spike14'] \
                            and df_row.iloc[0]['Close'] < df_row.iloc[0]['ema8']:
                        temp = temp[temp['Ticker'] != row.Ticker]
                        dict1.update({
                            'Entry_Date': row.Entry_Date,
                            'Signal': row.Signal,
                            'Ticker': row.Ticker,
                            'Entry_Price': row.Entry_Price,
                            'SL_Price': row.SL_Price,
                            'Qty': row.Qty,
                            'Exit_Date': d,
                            'Exit_Price': df_row.iloc[0]['Open'],
                            'Gain': ((df_row.iloc[0]['Open'] * row.Qty) / (row.Entry_Price * row.Qty) - 1) * 100,
                            'Gain_in_Dollars': (df_row.iloc[0]['Open'] * row.Qty) - (row.Entry_Price * row.Qty)
                        })
                        rows_list.append(dict1)
                    elif df_row.iloc[0]['Close'] < row.Entry_Price * 0.9 \
                            or df_row.iloc[0]['Close'] < df_row.iloc[0]['ema8']:
                        temp = temp[temp['Ticker'] != row.Ticker]
                        dict1.update({
                            'Entry_Date': row.Entry_Date,
                            'Signal': row.Signal,
                            'Ticker': row.Ticker,
                            'Entry_Price': row.Entry_Price,
                            'SL_Price': row.SL_Price,
                            'Qty': row.Qty,
                            'Exit_Date': d,
                            'Exit_Price': df_row.iloc[0]['Open'],
                            'Gain': ((df_row.iloc[0]['Open'] * row.Qty) / (row.Entry_Price * row.Qty) - 1) * 100,
                            'Gain_in_Dollars': (df_row.iloc[0]['Open'] * row.Qty) - (row.Entry_Price * row.Qty)
                        })
                        rows_list.append(dict1)
                else:
                    if df_row.iloc[0]['spike14'] \
                            and df_row.iloc[0]['Close'] > df_row.iloc[0]['ema8']:
                        temp = temp[temp['Ticker'] != row.Ticker]
                        dict1.update({
                            'Entry_Date': row.Entry_Date,
                            'Signal': row.Signal,
                            'Ticker': row.Ticker,
                            'Entry_Price': row.Entry_Price,
                            'SL_Price': row.SL_Price,
                            'Qty': row.Qty,
                            'Exit_Date': d,
                            'Exit_Price': df_row.iloc[0]['Open'],
                            'Gain': ((row.Entry_Price * row.Qty) / (df_row.iloc[0]['Open'] * row.Qty) - 1) * 100,
                            'Gain_in_Dollars': (row.Entry_Price * row.Qty) - (df_row.iloc[0]['Open'] * row.Qty)
                        })
                        rows_list.append(dict1)
                    elif df_row.iloc[0]['Close'] > row.Entry_Price * 1.1 \
                            or df_row.iloc[0]['Close'] > df_row.iloc[0]['ema8']:
                        temp = temp[temp['Ticker'] != row.Ticker]
                        dict1.update({
                            'Entry_Date': row.Entry_Date,
                            'Signal': row.Signal,
                            'Ticker': row.Ticker,
                            'Entry_Price': row.Entry_Price,
                            'SL_Price': row.SL_Price,
                            'Qty': row.Qty,
                            'Exit_Date': d,
                            'Exit_Price': df_row.iloc[0]['Open'],
                            'Gain': ((row.Entry_Price * row.Qty) / (df_row.iloc[0]['Open'] * row.Qty) - 1) * 100,
                            'Gain_in_Dollars': (row.Entry_Price * row.Qty) - (df_row.iloc[0]['Open'] * row.Qty)
                        })
                        rows_list.append(dict1)
        # print("SL triggered for ", rows_list.__len__(), " symbols")
        if len(self.closed_pos.index) == 0:
            self.closed_pos = pd.DataFrame(rows_list)
        else:
            self.closed_pos = pd.concat([self.closed_pos, pd.DataFrame(rows_list)])

        self.closed_pos = self.closed_pos.round(decimals=2)
        # self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.portfolio = temp
        # print(len(self.portfolio.index))

    def evaluate_new(self, start_date=""):
        ranked_files = glob.glob(self.rank_data_location + "*_*.csv")
        ranked_files.sort()
        i = 0
        is_long = True
        is_short = True
        max_positions = 40
        long_short_list = []
        for file in ranked_files[i:]:
            # Need just the basename to extract date from filename
            file_name = os.path.basename(file)
            # print(file_name)
            d = file_name[10:18]
            # print(d)
            df = pd.read_csv(file)
            # df = df[df['spike14'] == 0]

            long_df = df[df['rsi'] > 55]
            long_df = long_df[long_df['rsi5'] > 60]

            short_df = df[df['rsi'] < 35]
            short_df = short_df[short_df['rsi5'] < 30]

            long_df = long_df.sort_values(by=['rsi5'], ascending=False)
            short_df = short_df.sort_values(by=['rsi5'], ascending=True)

            # print(d, ",", len(long_df), ",", len(short_df))

            long_short_dict = {}
            long_short_dict = {
                'Date': d,
                'Long_count': len(long_df),
                'Short_count': len(short_df)
            }
            long_short_list.append(long_short_dict)
            # print(short_df)

            if d < start_date:
                continue

            if len(self.portfolio.index) > 0:
                self.check_for_sl(df, d)

            remaining_space = max_positions - len(self.portfolio.index)
            rows_list = []
            df = df[df['spike14'] == 0]
            if remaining_space > 0:
                for row in df.iterrows():
                    # print(type(row[1]))
                    # print(row[1])

                    if row[1].Ticker in self.portfolio.values:
                        continue
                    if row[1].rdx > 80:
                        signal = "Long"
                    elif row[1].rdx < 20:
                        signal = "SHORT"
                    dict1 = {
                        'Entry_Date': d,
                        'Signal': signal,
                        'Ticker': row[1].Ticker,
                        'Entry_Price': row[1].Open,
                        'SL_Price': row[1].ema8,
                        'Qty': round(5000 / row[1].Open),
                        'Exit_Date': '',
                        'Exit_Price': '',
                        'Gain': '',
                        'Gain_in_Dollars': ''
                    }
                    rows_list.append(dict1)
                    if rows_list.__len__() > remaining_space - 1:
                        break

                if len(self.portfolio.index) == 0:
                    self.portfolio = pd.DataFrame(rows_list)
                else:
                    self.portfolio = pd.concat([self.portfolio, pd.DataFrame(rows_list)])

            self.portfolio = self.portfolio.round(decimals=2)
            self.portfolio.to_csv("open_positions.csv", index=False)
        self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.long_short_df = pd.DataFrame(long_short_list)
        self.long_short_df.to_csv("LongShortCount.csv", index=False)
