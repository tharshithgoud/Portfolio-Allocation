import pandas as pd
import numpy as np

def generate_rolling_window(selected_financial_instruments,df,window_size):
  for ticker in selected_financial_instruments:
    log_returns = np.log(df[ticker]) - np.log(df[ticker].shift(1))
    df = pd.concat([df, log_returns.rename(ticker + '_log_returns')], axis=1)
    df[ticker+'_'+str(window_size)+'d_log_returns'] = df[ticker+'_log_returns'].rolling(window=window_size).sum() 
  k = 0
  flag = (len(df.index)%window_size)-1>window_size/2
  last_value_ticker = {}
  if flag:
    for ticker in selected_financial_instruments:
        last_value_ticker[ticker] = df[ticker+'_'+str(window_size)+'d_log_returns'].iloc[-1]
  for i,r in df.iterrows():
    if k%(window_size) != 0:
        for ticker in selected_financial_instruments:
          r[ticker+'_'+str(window_size)+'d_log_returns'] = pd.np.nan
    k+=1
  if flag:
    for ticker in selected_financial_instruments:
      df.iloc[-1][ticker+'_'+str(window_size)+'d_log_returns'] =last_value_ticker[ticker]
  for ticker in selected_financial_instruments:
    df[ticker] = df[ticker+'_'+str(window_size)+'d_log_returns']
  return df[selected_financial_instruments].dropna()