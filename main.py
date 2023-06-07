import streamlit as st
st.set_page_config(page_title="Portfolio Optimization",layout="wide",page_icon="https://www.algoanalytics.com/assets/images/logo.png")
import sys
sys.dont_write_bytecode = True
import json
import pandas as pd
from get_data import get_data_from_list
from rolling_window import generate_rolling_window
import numpy as np
from scipy.optimize import minimize
from markowitz import markowitz_portfolio

st.markdown('''
# Portfolio Optimization
''')
st.write('---')
output_container = st.empty()
st.sidebar.markdown(
    """
    <div style='text-align: center;'>
        <img style = 'width:80px' src='https://www.algoanalytics.com/assets/images/logo.png' alt='Algo Logo'>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.write('---') 
optimization_methods = ["Markowitz"]
optimization_method = st.sidebar.selectbox('Choose Optimization Method',optimization_methods)
years = st.sidebar.slider('Select Years',0,15,5)
date_df = pd.read_csv("historical_data/NIFTY 50.csv")
end_date = pd.to_datetime(date_df.iloc[0]["HistoricalDate"])
start_date = end_date - pd.DateOffset(days=30+years*365.4)
max_weight = st.sidebar.slider('Select Max Weight (%)',0,50,25)
# min_weight = st.sidebar.slider('Select Min Weight (%)',0,10,0)
window = st.sidebar.slider('Rolling Window',1,30,10)
data_used = ["Specific Index Stocks","Custom List","Choose Nifty Indices","Upload Data"]
data_choosen = st.sidebar.selectbox('Choose Data',data_used)
selected_financial_instruments = []

if data_choosen == "Custom List":
    list_input = st.sidebar.text_input("Enter all tickers/symbols","NIFTY 50,RELIANCE.NS,RAINBOW.NS,TCS.NS,AMZN,AAPL,ADANIENT.NS,TSLA,FACT.NS,VBL.NS")
    selected_financial_instruments = list_input.split(',')

if data_choosen == "Specific Index Stocks":
    print(start_date,end_date)
    index_type = []
    index_names = []
    index_symbols = []
    with open('tickers.json') as f:
        new_data_json = json.load(f)
    for i in new_data_json:
        index_type.append(i)
    option_index_type = st.sidebar.selectbox('Choose Index Type',index_type)
    for index in new_data_json[option_index_type]:
        index_names.append(index['index']) 
        index_symbols.append(index['indexSymbol'])
        
    option_index = st.sidebar.selectbox('Choose Index',index_names)
    target_index = None
    for i in range(len(new_data_json[option_index_type])):
        if new_data_json[option_index_type][i]['index'] == option_index:
            target_index = new_data_json[option_index_type][i]
            break
    index_symbol = target_index['indexSymbol']
    index_stock_tickers = target_index['stockList']
    selected_financial_instruments = index_stock_tickers

if data_choosen == "Choose Nifty Indices":
    index_symbols = []
    with open('tickers.json') as f:
        new_data_json = json.load(f)
    for index_group in new_data_json:
        for index in new_data_json[index_group]:
            index_symbols.append(index['indexSymbol'])
    index_symbols.remove("NIFTY200MOMENTM30")
    if years > 5: 
        delete_indices_list = ["NIFTY GROWSECT 15","NIFTY100 QUALTY30","NIFTY50 VALUE 20","NIFTY200MOMENTM30","NIFTY100 LIQ 15","NIFTY MID LIQ 15","NIFTY INDIA DEFENCE"]
        for symbol in delete_indices_list:
            if symbol in index_symbols:
                index_symbols.remove(symbol)
        selected_indices = st.multiselect('Select Stocks', index_symbols,default=index_symbols)
        selected_financial_instruments = selected_indices
    else:
        selected_indices = st.multiselect('Select Stocks', index_symbols,default=index_symbols)
        selected_financial_instruments = selected_indices


if data_choosen == "Upload Data":
    try:
        uploaded_file = st.file_uploader("Upload a file which contains a column named Financial Instrument and the values of the column should be the ticker/symbols of stocks/indices (CSV/XLSX) / Ignore division/0 Error and procees to upload your file", type=["csv", "xlsx"])
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)
        selected_financial_instruments = df['Financial Instrument'].values
    except:
        print("Waiting For Uploading")

df_fetched = get_data_from_list(start_date,end_date,selected_financial_instruments)

selected_financial_instruments = list(selected_financial_instruments)

columns_to_drop = []
for column in df_fetched.columns:
    if df_fetched[column].isna().sum() > 30:
        columns_to_drop.append(column)
        selected_financial_instruments.remove(column)
df_fetched.drop(columns_to_drop, axis=1, inplace=True)

if window > 1:    
    df_rolling_window = generate_rolling_window(selected_financial_instruments, df_fetched, window)
else:
    df_rolling_window = np.log(df_fetched / df_fetched.shift(1)).dropna()

if optimization_method == 'Markowitz':
    init_weights = np.array([1 / len(selected_financial_instruments)] * len(selected_financial_instruments))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = [(0, max_weight/100)] * len(selected_financial_instruments)
    result = minimize(markowitz_portfolio, init_weights, args=(df_rolling_window), method='SLSQP', bounds=bounds, constraints=constraints)
    opt_weights = result.x
    dict = {}
    all_instruments = df_rolling_window.columns
    for i in range(len(all_instruments)):
        dict[all_instruments[i]] = round(opt_weights[i],4)*100
    df = pd.DataFrame(dict.items(), columns=["Index", "Allocation %"])
    df = df.sort_values(by="Allocation %",ascending=False)
    st.download_button(
        "Download Results in CSV",
        df.to_csv(index=False),
        "Portfolio-Allocation.csv",
        "text/csv",
        key='download-results-csv'
    )
    st.dataframe(df,height = 600,use_container_width=True)


st.subheader("The Below Tables are shown for verification purpose, will be deleted later after validating the project process flow and results!")
st.subheader("Table - 1 (Raw Data - Adj Close)")
st.dataframe(df_fetched,height = 600,use_container_width=True)
st.subheader("Table - 2 (After Log Returns and Rolling window)")
st.dataframe(df_rolling_window,height = 600,use_container_width=True)



