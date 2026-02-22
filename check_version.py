import MetaTrader5 as mt5
def check():
    if not mt5.initialize():
        print(f"Init failed: {mt5.last_error()}")
    else:
        print(f"MT5 version: {mt5.version()}")
        mt5.shutdown()
if __name__ == "__main__":
    check()
