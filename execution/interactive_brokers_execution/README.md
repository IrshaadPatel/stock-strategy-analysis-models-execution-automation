
# Interactive Brokers Auto-Trading Bot

This Python script is an example of an auto-trading bot using the Interactive Brokers (IB) API. It monitors the real-time price of a specified stock (in this case, TSLA) and places a buy order when certain conditions are met. This README provides an overview of the code and how to use it. This is a very simplistic script just to demonstrate the execution framework. For better results, a custom model or signal based framework would be implemented to make better informed trades.

## Prerequisites

Before running the script, you need to ensure that you have the following prerequisites:

1. An Interactive Brokers account.
2. IB API client ID.
3. [IB API](https://interactivebrokers.github.io/) installed.
4. Python 3.x installed on your machine.

## Configuration

Before running the script, you should modify the following variables in the code to match your specific configuration:

- `account_id`: Replace with your Interactive Brokers account ID.
- `client_id`: Replace with your IB API client ID.

## Implementation Details

The code is structured as follows:

- Import necessary modules, including `EClient`, `EWrapper`, `Contract`, `ContractDetails`, and `Order` from the IB API, and import the `sleep` function.

- Define the `MyWrapper` class, which is a custom wrapper class that inherits from `EWrapper`. This class handles the logic for monitoring and trading TSLA stock.

- Inside `MyWrapper`, there is a `monitor_prices` method that continuously monitors the real-time and opening prices of TSLA. When the current price falls below 80% of the opening price, it places a buy order.

- The `place_buy_order` method creates a contract and order object for placing a buy order for TSLA stock.

- `get_real_time_price` and `get_opening_price` are placeholder functions that need to be implemented to fetch real-time and opening prices. You can use data providers or APIs for this purpose.

- In the `main` function, an instance of the `EClient` class with `MyWrapper` as its wrapper is created. It connects to the IB TWS or IB Gateway and requests the next valid order ID. Then, it starts the event loop using `app.run()`.

## Usage

1. Configure the script by setting your `account_id` and `client_id`.

2. Implement the `get_real_time_price` and `get_opening_price` functions to fetch real-time and opening prices. You may use third-party data providers or APIs for this purpose.

3. Run the script using Python 3.x:

   ```bash
   python script_name.py
   ```

4. The script will connect to your Interactive Brokers account, monitor TSLA prices, and place buy orders when conditions are met.


---

Feel free to customize and expand this README as needed for your specific use case or audience. Additionally, make sure to implement the `get_real_time_price` and `get_opening_price` functions to fetch the required data for your trading strategy.
