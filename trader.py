import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()

class GoldTrader:
    def __init__(self):
        self.login = int(os.getenv("MT5_LOGIN"))
        self.password = os.getenv("MT5_PASSWORD")
        self.server = os.getenv("MT5_SERVER")
        self.symbol = "XAUUSD"

    async def initialize(self):
        """Initializes the MetaTrader 5 connection."""
        print(f"Connecting to MT5 Terminal for {self.login}...")
        
        if not mt5.initialize():
            print(f"MT5 initialize() failed, error code: {mt5.last_error()}")
            return False

        # Try to login
        authorized = mt5.login(self.login, password=self.password, server=self.server)
        if authorized:
            print(f"Connected to MT5 account {self.login}")
            return True
        else:
            print(f"Failed to connect to account {self.login}, error code: {mt5.last_error()}")
            return False

    async def get_market_snapshot(self, symbol="XAUUSD"):
        """Fetches the latest tick and account info from MT5."""
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return f"Error: Cannot find symbol {symbol}"
        
        account_info = mt5.account_info()
        balance = account_info.balance if account_info else "N/A"
        
        return f"Symbol: {symbol}, Bid: {tick.bid}, Ask: {tick.ask}, Balance: ${balance}"

    async def execute_trade(self, action, volume=0.01):
        """Executes a market order on MT5."""
        if action not in ["BUY", "SELL"]:
            return

        order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.symbol).ask if action == "BUY" else mt5.symbol_info_tick(self.symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "magic": 123456,
            "comment": "AI Gold Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        print(f"Sending {action} order for {volume} lots...")
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed, retcode: {result.retcode}")
        else:
            print(f"Order successful! Ticket: {result.order}")

    async def close(self):
        mt5.shutdown()

if __name__ == "__main__":
    # Test (Standard synchronous wrapper for MT5 testing)
    import asyncio
    trader = GoldTrader()
    asyncio.run(trader.initialize())
