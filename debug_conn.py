import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

def debug_connection():
    terminal_path = r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe"
    
    login = int(os.getenv('MT5_LOGIN'))
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')

    if not mt5.initialize(path=terminal_path, login=login, password=password, server=server):
        print(f"MT5 Combined Init/Login Failed: {mt5.last_error()}")
        return
    
    print(f"Successfully connected to {login}")
    account_info = mt5.account_info()
    print(f"Account Info: {account_info._asdict() if account_info else 'None'}")
    
    mt5.shutdown()

if __name__ == "__main__":
    debug_connection()
