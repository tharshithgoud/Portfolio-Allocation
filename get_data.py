import yfinance as yf
import pandas as pd
import warnings


def swap_elements(lst, n):
    if n >= len(lst):
        return lst 
    lst[0], lst[n] = lst[n], lst[0]
    return lst

def get_data_from_list(start_date,end_date,stock_list):
    warnings.filterwarnings('ignore')
    nifty_tickers = []
    yfinance_tickers = []
    for ticker in stock_list:
        is_nifty = ticker.replace(" ", "")[:5].lower() == "nifty"
        if is_nifty:
            nifty_tickers.append(ticker)
        else:
            yfinance_tickers.append(ticker)
    num_seconds = (end_date - start_date).total_seconds()
    num_years = num_seconds / (365.25 * 24 * 60 * 60)
    length_check = num_years*236
    for i in range(1,len(yfinance_tickers)):
        check_df = yf.download(yfinance_tickers[0],start_date,end_date)['Adj Close']
        if len(check_df) > length_check:
            break
        else:
            yfinance_tickers[0],yfinance_tickers[i] = yfinance_tickers[i],yfinance_tickers[0]

    if len(yfinance_tickers) != 0:
        yfinance_data = yf.download(yfinance_tickers,start_date,end_date)['Adj Close']
    merged_nse_df = pd.DataFrame()
    for ticker in nifty_tickers:
        data = pd.read_csv("historical_data/"+ticker+".csv")
        data = data[data['INDEX_NAME'].str.upper() == ticker.upper()]
        df_nse_index = data[["HistoricalDate","CLOSE"]]
        df_nse_index[ticker] = df_nse_index["CLOSE"]
        df_nse_index = df_nse_index.drop_duplicates(subset='HistoricalDate')
        df_nse_index = df_nse_index[["HistoricalDate",ticker]]
        df_nse_index["Date"] = pd.to_datetime(df_nse_index["HistoricalDate"])
        df_nse_index = df_nse_index.sort_values(by="Date", ascending=True)
        df_nse_index = df_nse_index[(df_nse_index["Date"] >= start_date) & (df_nse_index["Date"] <= end_date)]
        df_nse_index.index = df_nse_index["Date"]
        df_nse_index = df_nse_index[[ticker]]
        if merged_nse_df.empty:
            merged_nse_df.index = df_nse_index.index
        merged_nse_df = pd.merge(merged_nse_df, df_nse_index, left_index=True, right_index=True, how="left")
    if len(nifty_tickers)==0 and len(yfinance_tickers)>0:
        return yfinance_data
    elif len(nifty_tickers)>0 and len(yfinance_tickers)==0:
        return merged_nse_df
    elif len(nifty_tickers)==0 and len(yfinance_tickers)==0:
        return pd.DataFrame()
    else:
        final_merged_df = pd.merge(merged_nse_df, yfinance_data, left_index=True, right_index=True, how="left").ffill()
        return final_merged_df.dropna()





