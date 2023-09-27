from time import sleep
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ContractDetails
from ibapi.order import Order

# Define your Interactive Brokers account details and contract details for TSLA
account_id = "YOUR_ACCOUNT_ID"
client_id = 1  # Your IB API client ID
app = None

class MyWrapper(EWrapper):
    def __init__(self):
        self.order_id = 1

    def nextValidId(self, orderId: int):
        self.order_id = orderId
        self.monitor_prices()

    def monitor_prices(self):
        while True:
            current_price = get_real_time_price("TSLA")  # Get real-time price of TSLA
            opening_price = get_opening_price("TSLA")  # Get opening price of TSLA
            
            if current_price <= opening_price * 0.8:
                self.place_buy_order(current_price)
            
            # Sleep for a short period (e.g., 5 seconds) before checking again
            sleep(5)

    def place_buy_order(self, price):
        contract = Contract()
        contract.symbol = "TSLA"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        order = Order()
        order.action = "BUY"
        order.totalQuantity = 1  # Number of shares to buy
        order.orderType = "LMT"  # Limit order type
        order.lmtPrice = price

        app.placeOrder(self.order_id, contract, order)

def get_real_time_price(symbol):
    # You need to implement a function to fetch the real-time price of TSLA
    # This could be done using a data provider or API

def get_opening_price(symbol):
    # You need to implement a function to fetch the opening price of TSLA
    # This could be done using historical data or a data provider

def main():
    global app
    app = EClient(MyWrapper())
    app.connect("127.0.0.1", 7497, client_id)  # Connect to IB TWS or IB Gateway

    app.reqIds(-1)  # Request the next valid order ID

    app.run()

if __name__ == "__main__":
    main()
