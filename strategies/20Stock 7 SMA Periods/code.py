import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Define the list of stock symbols
stocklist = ['SPY', 'QQQ', 'TSLA', 'AAPL', 'NVDA', 'GOOG', 'BAC', 'COST', 'F', 'MSFT', 'AMZN', 'BRK-B', 'META',
            'V', 'XOM', 'WMT', 'TSM', 'JPM', 'JNJ', 'PEP']

# Create a dictionary to store DataFrames
dataframes = {}

# Define the date range
start_date = "2018-01-01"
end_date = "2023-08-01"

# List of different MA period combinations
ma_periods = [(2, 5), (4, 10), (5, 14), (8, 20), (10, 28), (16, 40), (30, 75)]

# Loop through the stock symbols and create DataFrames
for symbol in stocklist:
    # Fetch data from Yahoo Finance
    df = yf.download(symbol, start=start_date, end=end_date)

    # Rename the DataFrame with the stock symbol
    df.name = f'df_{symbol}'

    # Store the DataFrame in the dictionary
    dataframes[df.name] = df

# Create a list to store results DataFrames
results_dfs = []

# Loop through each stock
for symbol in stocklist:
    df_name = f'df_{symbol}'
    df = dataframes[df_name]

    for short_period, long_period in ma_periods:
        # Calculate the short and long-term moving averages
        df[f'{short_period}_Day_MA'] = df['Close'].rolling(window=short_period).mean()
        df[f'{long_period}_Day_MA'] = df['Close'].rolling(window=long_period).mean()

        # Initialize a column for holding signals
        df['Signal'] = 0

        # Generate buy signals (short-term MA crosses above long-term MA)
        df.loc[df[f'{short_period}_Day_MA'] > df[f'{long_period}_Day_MA'], 'Signal'] = 1  # 1 means buy

        # Generate sell signals (short-term MA crosses below long-term MA)
        df.loc[df[f'{short_period}_Day_MA'] < df[f'{long_period}_Day_MA'], 'Signal'] = -1  # -1 means sell

        # Calculate the cumulative return for this period
        cumulative_return = (df['Signal'].shift(1) * df['Close'].pct_change() + 1).cumprod()
        total_return_percentage = (cumulative_return.iloc[-1] - 1) * 100

        # Create a result DataFrame and append it to the list
        result_df = pd.DataFrame({'Stock': [symbol], 'MA Period': [f'{short_period}/{long_period}'], 'Total Return %': [total_return_percentage]})
        results_dfs.append(result_df)

# Concatenate all result DataFrames into one
results_df = pd.concat(results_dfs, ignore_index=True)

#compare for each stock and their best SMA period crossover strategy if it is actually worth implmenting the strategy
#or if you would just make more money holding the stock
###


df = pd.DataFrame(results_df)

# Group by 'Stock' and find the row with the maximum 'Total Return %'
max_return_rows = df.groupby('Stock')['Total Return %'].idxmax()
max_return_data = df.loc[max_return_rows, ['Stock', 'MA Period', 'Total Return %']]
max_return_data = max_return_data.sort_values(by='Total Return %', ascending=False)
max_return_data.reset_index(drop=True, inplace=True)
max_return_data.index += 1

for symbol in stocklist:
    df_name = f'df_{symbol}'
    df = dataframes[df_name]
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    price_percent_change = ((end_price - start_price) / start_price) * 100
    max_return_data.loc[max_return_data['Stock'] == symbol, 'Price % Change'] = price_percent_change
    
max_return_data['Return - Price Difference'] = max_return_data['Total Return %'] - max_return_data['Price % Change']
# Print the updated max_return_data DataFrame
print(max_return_data)
