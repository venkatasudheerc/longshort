import glob
import pandas as pd


class Strategy:
    def __init__(self, data_loc="./weekly/rank_data"):
        self.rank_data_location = "./rank_data/"
        self.portfolio = pd.DataFrame()
        self.closed_pos = pd.DataFrame()
        self.long_short_df = pd.DataFrame()
        self.cnt_max_open_pos = 0
        self.realized_gain = 0
        self.unrealized_gain = 0
        self.is_long_only = True
        self.index_df = pd.DataFrame()

    def load_index(self, index_file="./stock_data/SPY.csv"):
        signal = "LONG"
        df = pd.read_csv(index_file)
        self.index_df = pd.DataFrame(columns=['Date', 'signal'])
        row_list = []
        for index, row in df.iterrows():
            dict1 = {}
            '''
            # MACD and RDX check
            if row.macd_diff > 0:
                if row.rdx > 50:
                    signal = "LONG"
            else:
                if row.rdx < 50:
                    signal = "SHORT"
            '''
            if row.ema8 > row.ema21:
                signal = "LONG"
            elif row.ema8 < row.ema21:
                signal = "SHORT"

            dict1.update({
                'Date': str(row.Date[:10]).replace("-", ""),
                'signal': signal
            })
            row_list.append(dict1)

        self.index_df = pd.DataFrame(row_list)
        self.index_df.to_csv("SPY_signal.csv", index=False)

    def check_for_stoploss(self, df, d):
        temp = self.portfolio
        rows_list = []
        # print("Checking SL for ", d)
        for index, row in self.portfolio.iterrows():
            # print(index, " : ", row.Ticker)
            dict1 = {}
            if row.Ticker in df.values:
                df_row = df[df['Ticker'] == row.Ticker]
                if df_row.iloc[0]['Close'] < df_row.iloc[0]['ema21']:
                    temp = temp[temp['Ticker'] != row.Ticker]
                    dict1.update({
                        'Entry_Date': row.Entry_Date,
                        'Signal': row.Signal,
                        'Ticker': row.Ticker,
                        'Entry_Price': row.Entry_Price,
                        'Qty': row.Qty,
                        'Exit_Date': d,
                        'Exit_Price': df_row.iloc[0]['Open'],
                        'Gain': ((df_row.iloc[0]['Open']*row.Qty) / (row.Entry_Price*row.Qty) - 1)*100
                    })
                    rows_list.append(dict1)
        # print("SL triggered for ", rows_list.__len__(), " symbols")
        if len(self.closed_pos.index) == 0:
            self.closed_pos = pd.DataFrame(rows_list)
        else:
            self.closed_pos = pd.concat([self.closed_pos, pd.DataFrame(rows_list)])

        self.closed_pos = self.closed_pos.round(decimals=2)
        self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.portfolio = temp
        # print(len(self.portfolio.index))

    def check_for_short_stoploss(self, df, d):
        temp = self.portfolio
        rows_list = []
        # print("Checking SL for ", d)
        for index, row in self.portfolio.iterrows():
            # print(index, " : ", row.Ticker)
            dict1 = {}
            if row.Ticker in df.values:
                df_row = df[df['Ticker'] == row.Ticker]
                if df_row.iloc[0]['Close'] > df_row.iloc[0]['ema21']:
                    temp = temp[temp['Ticker'] != row.Ticker]
                    dict1.update({
                        'Entry_Date': row.Entry_Date,
                        'Signal': row.Signal,
                        'Ticker': row.Ticker,
                        'Entry_Price': row.Entry_Price,
                        'Qty': row.Qty,
                        'Exit_Date': d,
                        'Exit_Price': df_row.iloc[0]['Open'],
                        'Gain': ((row.Entry_Price*row.Qty) / (df_row.iloc[0]['Open']*row.Qty) - 1)*100
                    })
                    rows_list.append(dict1)
        # print("SL triggered for ", rows_list.__len__(), " symbols")
        if len(self.closed_pos.index) == 0:
            self.closed_pos = pd.DataFrame(rows_list)
        else:
            self.closed_pos = pd.concat([self.closed_pos, pd.DataFrame(rows_list)])

        self.closed_pos = self.closed_pos.round(decimals=2)
        self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.portfolio = temp
        # print(len(self.portfolio.index))

    def exit_current_portfolio(self, df, d):
        temp = self.portfolio
        rows_list = []
        print("Exiting All positions on ", d)
        for index, row in self.portfolio.iterrows():
            # print(index, " : ", row.Ticker)
            dict1 = {}
            if row.Ticker in df.values:
                df_row = df[df['Ticker'] == row.Ticker]
                if True:
                    temp = temp[temp['Ticker'] != row.Ticker]
                    gain = 0
                    if self.is_long_only:
                        gain = ((df_row.iloc[0]['Open']*row.Qty)/(row.Entry_Price*row.Qty) - 1)*100
                    else:
                        gain = ((row.Entry_Price*row.Qty) / (df_row.iloc[0]['Open']*row.Qty) - 1)*100

                    dict1.update({
                        'Entry_Date': row.Entry_Date,
                        'Signal': row.Signal,
                        'Ticker': row.Ticker,
                        'Entry_Price': row.Entry_Price,
                        'Qty': row.Qty,
                        'Exit_Date': d,
                        'Exit_Price': df_row.iloc[0]['Open'],
                        'Gain': gain
                    })
                    rows_list.append(dict1)
        # print("SL triggered for ", rows_list.__len__(), " symbols")
        if len(self.closed_pos.index) == 0:
            self.closed_pos = pd.DataFrame(rows_list)
        else:
            self.closed_pos = pd.concat([self.closed_pos, pd.DataFrame(rows_list)])

        self.closed_pos = self.closed_pos.round(decimals=2)
        self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.portfolio = temp
        # print(len(self.portfolio.index))

    def check_rsi_based_sl(self, df, d):
        temp = self.portfolio
        rows_list = []
        print("length (before checking for SL) : ", len(self.portfolio.index))
        print("Checking SL for ", d)
        for index, row in self.portfolio.iterrows():
            # print(index, " : ", row.Ticker)
            dict1 = {}
            if row.Ticker in df.values:
                df_row = df[df['Ticker'] == row.Ticker]
                if df_row.iloc[0]['Close'] < row.Entry_Price*0.9 \
                        or df_row.iloc[0]['Close'] < df_row.iloc[0]['ema21']:
                    temp = temp[temp['Ticker'] != row.Ticker]
                    dict1.update({
                        'Entry_Date': row.Entry_Date,
                        'Ticker': row.Ticker,
                        'Entry_Price': row.Entry_Price,
                        'Exit_Date': d,
                        'Exit_Price': df_row.iloc[0]['Open'],
                        'Gain': df_row.iloc[0]['Open'] / row.Entry_Price - 1
                    })
                    rows_list.append(dict1)
        print("SL triggered for ", rows_list.__len__(), " symbols")
        if len(self.closed_pos.index) == 0:
            self.closed_pos = pd.DataFrame(rows_list)
        else:
            self.closed_pos = pd.concat([self.closed_pos, pd.DataFrame(rows_list)])

        self.closed_pos = self.closed_pos.round(decimals=2)
        self.closed_pos.to_csv("closed_positions.csv", index=False)
        self.portfolio = temp.reset_index(drop=True)
        print("length (After checking for SL) : ", len(self.portfolio.index))

    def evaluate(self):
        ranked_files = glob.glob(self.rank_data_location + "*_*.csv")
        ranked_files.sort()
        i = 0
        max_positions = 5
        long_short_dict = {}
        long_short_list = []
        for file in ranked_files[i:]:
            # print(file)
            d = file[22:30]
            # print(d)
            df = pd.read_csv(file)
            long_df = df[df['rdx'] > 80]
            short_df = df[df['rdx'] < 25]
            long_df = long_df.sort_values(by=['rdx'], ascending=False)
            short_df = short_df.sort_values(by=['rdx'], ascending=True)
            # print(d, ",", len(long_df), ",", len(short_df))

            long_short_dict = {
                'Date': d,
                'Long_count': len(long_df),
                'Short_count': len(short_df)
            }
            long_short_list.append(long_short_dict)

            self.index_df.reset_index(drop=True, inplace=True)
            for index, row in self.index_df.iterrows():
                if row.Date < d:
                    continue
                elif row.Date <= d:
                    is_long = True if row.signal == "LONG" else False
                    if is_long != self.is_long_only:
                        if len(self.portfolio.index) > 0:
                            self.exit_current_portfolio(df, d)
                        self.is_long_only = is_long
                else:
                    break

            # print(short_df)

            if self.is_long_only:
                if len(self.portfolio.index) > 0:
                    self.check_for_stoploss(df, d)

                remaining_space = max_positions - len(self.portfolio.index)
                rows_list = []
                if remaining_space > 0:
                    for row in long_df.iterrows():
                        # print(type(row[1]))
                        # print(row[1])

                        if row[1].Ticker in self.portfolio.values:
                            continue

                        dict1 = {
                            'Entry_Date': d,
                            'Signal': "Long" if self.is_long_only else "SHORT",
                            'Ticker': row[1].Ticker,
                            'Entry_Price': row[1].Open,
                            'Qty': 5000/row[1].Open,
                            'Exit_Date': '',
                            'Exit_Price': '',
                            'Gain': ''
                        }
                        rows_list.append(dict1)
                        if rows_list.__len__() > remaining_space-1:
                            break

                    if len(self.portfolio.index) == 0:
                        self.portfolio = pd.DataFrame(rows_list)
                    else:
                        self.portfolio = pd.concat([self.portfolio, pd.DataFrame(rows_list)])
            else:
                if len(self.portfolio.index) > 0:
                    self.check_for_short_stoploss(df, d)

                remaining_space = max_positions - len(self.portfolio.index)
                # print(self.portfolio)
                rows_list = []
                if remaining_space > 0:
                    for row in short_df.iterrows():
                        # print(type(row[1]))
                        # print(row[1])

                        if row[1].Ticker in self.portfolio.values:
                            continue

                        dict1 = {
                            'Entry_Date': d,
                            'Signal': "Long" if self.is_long_only else "SHORT",
                            'Ticker': row[1].Ticker,
                            'Entry_Price': row[1].Open,
                            'Qty': 5000 / row[1].Open,
                            'Exit_Date': '',
                            'Exit_Price': '',
                            'Gain': ''
                        }
                        rows_list.append(dict1)
                        if rows_list.__len__() > remaining_space-1:
                            break

                    if len(self.portfolio.index) == 0:
                        self.portfolio = pd.DataFrame(rows_list)
                    else:
                        self.portfolio = pd.concat([self.portfolio, pd.DataFrame(rows_list)])
                    # print(self.portfolio)
            self.portfolio.to_csv("open_positions.csv", index=False)
        self.long_short_df = pd.DataFrame(long_short_list)
        self.long_short_df.to_csv("LongShortCount.csv", index=False)



