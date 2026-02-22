import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

def check():
    if not mt5.initialize():
        print(f"MT5 Init Failed: {mt5.last_error()}")
        return

    login = int(os.getenv('MT5_LOGIN'))
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')
    
    authorized = mt5.login(login, password=password, server=server)
    if not authorized:
        print(f"Login Failed for {login}: {mt5.last_error()}")
        mt5.shutdown()
        return
        
    print(f"Successfully connected to {login}")
    symbols = mt5.symbols_get()
    if symbols:
        gold_names = [s.name for s in symbols if "XAU" in s.name]
        print(f"Available Gold Symbols: {gold_names}")
    else:
        print("No symbols found.")
    
    mt5.shutdown()

if __name__ == "__main__":
    check()
