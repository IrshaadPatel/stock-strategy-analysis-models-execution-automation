
#import libraries

import requests
import pandas as pd
import numpy as np
import json 
import matplotlib.pyplot as plt
import tweepy
import pandas_ta as pta
import datetime
pd.set_option('display.max_rows', None)



#initialize twitter authentication keys 

bearer_token = "replace_with_yours"
consumer_key = "replace_with_yours"
consumer_secret = "replace_with_yours"
access_token = "replace_with_yours"
access_token_secret = "replace_with_yours"



# Authenticate to Twitter
client = tweepy.Client(bearer_token=bearer_token)
 
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)



#authenticate to marketstack API to pull intraday data by the minute. Set up data query for multiple stocks, convert from JSON raw data and create a unique dataframe for each stock

today = datetime.date.today().strftime("%Y-%-m-%-d")

params = {
    'access_key': 'replace_with_yours',
    'interval': '1min',
    'date_from': f'{today}T13:30:00+0000',
    'date_to': f'{today}T20:00:00+0000',
    'limit': 100000
}

stocklist = ['SPY', 'QQQ', 'TSLA', 'AAPL', 'NVDA', 'GOOG', 'BAC', 'COST', 'F']

dfs = []
for stock in stocklist:
    url = f'https://api.marketstack.com/v1/tickers/{stock}/intraday'
    api_query = requests.get(url, params=params)
    stock_data = api_query.json()
    datapull = []
    for ticker in stock_data['data']['intraday']:
        datapull.append(ticker)
    
    # Clean data and create a unique dataframe for each stock
    df = pd.DataFrame(datapull)
    df_name = f"df_{stock.lower()}"
    globals()[df_name] = df
    dfs.append(df_name)




#clean data, format and add VOLUME DIFFERENTIAL column which represents 1 minute volume
for df_name in dfs:
    df = globals()[df_name]
    df['Calendar Date'] = df['date'].str[:10]
    df['Time'] = df['date'].str[11:19]
    df['datetime'] = df['date']
    df.drop(['date'], axis=1, inplace=True)
    df_clean = df.dropna()
    df_ordered = df_clean.iloc[::-1]
    use2 = df_ordered.copy()
    use2.reset_index(drop=True, inplace=True)

    ##calculate voldiff, this is needed for intraday data as a cumulative total is provided. A difference between 2 intervals results in the volume for each minute segment.
    use2['voldiff'] = 0

    #2 AM volume is a bunch of noise (10 digit numbers? this filters it out)
    for i in range(len(use2)):
        if use2['datetime'][i][12:19]=="2:00:00":
            use2['volume'][i] = 0

    #Calculate volume difference as volume is cumulative. this only subtracts the next segments volume if the date is the same. 
    for i in range(len(use2)):
        try:
            if use2['datetime'][i][0:10] == use2['datetime'][i+1][0:10]:
                use2['voldiff'][i] = use2.shift(-1)['volume'][i] - use2['volume'][i]
            else:
                use2['voldiff'][i] = use2['volume'][i+1]
        except:
            pass

    use2['voldiff'] = use2.voldiff.shift(1)
    use2.reset_index(drop=True, inplace=True)
    use2.loc[0, 'voldiff'] = use2.loc[0, 'volume']
    
    globals()[df_name] = use2




#this code inputs the RSI and VWAP information into the dataframe, key indicators for stock market analysis using the PTA library

for df_name in dfs:
    df = globals()[df_name]
    df.set_index(pd.DatetimeIndex(df["datetime"]), inplace=True)
    VWAP = pta.vwap(df["high"], df["low"], df["last"], df["voldiff"], anchor='1T')
    df.insert(loc=0, column='VWAP', value=VWAP)
    df.reset_index(drop=True, inplace=True)
    RSI = pta.rsi(df['last'])
    df.insert(loc=0, column='RSI', value=RSI)
    df['Time EST'] = df['Time'] - pd.Timedelta(hours=4)
    df['VWAP'] = df['VWAP'].round(2)
    try:
        df['RSI'] = df['RSI'].round(2)
    except:
        pass





#this is the logic to calculate VWAP direction (when price is > VWAP it is a bullish cross and you want to buy. When price is falls below VWAP it is bearish and you should sell)

for df_name in dfs:
    df = globals()[df_name] # get the dataframe using the name
    df['vwap_direction'] = 0
    for i in range(len(df)):
        if df['VWAP'][i] > df['last'][i]:
            df['vwap_direction'][i] = 0
        else:
            df['vwap_direction'][i] = 1






#this is the logic for calculating the VWAP signal (when price is > VWAP then it is a bullish signal. when price is below VWAP it is bearish, the signal is then triggered when a change in VWAP direction occurs)

for df_name in dfs:
    df = globals()[df_name] # get the dataframe using the name
    df['vwap_signal'] = 0
    for i in range(len(df)):
        try:
            if df['vwap_direction'][i] == 1 and df['vwap_direction'][i+1] == 1:
                df['vwap_signal'][i+1] = 0
            elif df['vwap_direction'][i] == 1 and df['vwap_direction'][i+1] == 0:
                df['vwap_signal'][i+1] = -1
            elif df['vwap_direction'][i] == 0 and df['vwap_direction'][i+1] == 1:
                df['vwap_signal'][i+1] = 1
            elif df['vwap_direction'][i] == 0 and df['vwap_direction'][i+1] == 0:
                df['vwap_signal'][i+1] = 0
        except:
            pass






#this code posts on twitter using create_tweet by looking at the VWAP signal and grabbing relevant data when a crossover event occurs. The data is then formatted so that only relevant information accompanies the alert

for df_name in dfs:
    df = globals()[df_name] # get the dataframe using the name
    for i in range(len(df) - 5, len(df)):
        try:
            # Check if the VWAP signal is 1 and the VWAP direction is the same as the next row
            if df.loc[i, 'vwap_signal'] == 1 and df.loc[i, 'vwap_direction'] == df.loc[i+1, 'vwap_direction'] == df.loc[i+2,'vwap_direction'] == df.loc[i+3,'vwap_direction'] == df.loc[i+4,'vwap_direction']:
                client.create_tweet(text=('Stock' + ': ' +'$'+ str(df.loc[i, 'symbol']) + '\n'
                                  + 'Signal Type' + ': ' + 'Bullish' + '\n'
                                  + 'Indicator' + ': ' + 'VWAP Crossover'  + '\n' # Fixed formatting
                                  + 'VWAP' + ': ' + str(df.loc[i, 'VWAP']) + '\n'
                                  + 'Time of initial cross EST' + ': ' + str(df.loc[i, 'Time EST'])[7:15] + '\n' # Fixed syntax error
                                  + 'Price at initial cross' + ': ' + str(df.loc[i, 'last']) + '\n'
                                  + 'Price now' + ': ' + str(df.loc[i+4, 'last']) + '\n'
                                  + 'RSI' + ': ' + str(df.loc[i, 'RSI']) + '\n'))
            # Check if the VWAP signal is -1 and the VWAP direction is the same as the next row
            elif df.loc[i, 'vwap_signal'] == -1 and df.loc[i, 'vwap_direction'] == df.loc[i+1, 'vwap_direction'] == df.loc[i+2,'vwap_direction'] == df.loc[i+3,'vwap_direction'] == df.loc[i+4,'vwap_direction']:
                 client.create_tweet(text=('Stock' + ': '+'$' + str(df.loc[i, 'symbol']) + '\n'
                                  + 'Signal Type' + ': ' + 'Bearish' + '\n'
                                  + 'Indicator' + ': ' + 'VWAP Crossover' + '\n' # Fixed formatting
                                  + 'VWAP' + ': ' + str(df.loc[i, 'VWAP']) + '\n'
                                  + 'Time of initial cross EST' + ': ' + str(df.loc[i, 'Time EST'])[7:15] + '\n' # Fixed syntax error
                                  + 'Price at initial cross' + ': ' + str(df.loc[i, 'last']) + '\n'
                                  + 'Price now' + ': ' + str(df.loc[i+4, 'last']) + '\n'
                                  + 'RSI' + ': ' + str(df.loc[i, 'RSI']) + '\n'))
        except:
            pass
