import os
import MetaTrader5 as mt5
from dotenv import load_dotenv
import sqlite3
import json

load_dotenv()

class GoldTrader:
    def __init__(self):
        self.login = int(os.getenv("MT5_LOGIN"))
        self.password = os.getenv("MT5_PASSWORD")
        self.server = os.getenv("MT5_SERVER")
        self.symbol = os.getenv("SYMBOL", "XAUUSDm")
        self.risk_percent = float(os.getenv("RISK_PERCENT", "1.0")) / 100.0
        # Exness explicit terminal path for reliability
        self.terminal_path = r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe"
        
        # Advanced Settings
        self.max_spread = float(os.getenv("MAX_SPREAD", "40"))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT_PERCENT", "2.0")) / 100.0
        self.start_hour = int(os.getenv("START_HOUR", "0"))
        self.end_hour = int(os.getenv("END_HOUR", "23"))
        
        # Telegram Setup
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # Trailing stop settings (in points)
        self.trailing_stop_dist = 300  # 30 pips
        self.trailing_step = 50       # 5 pips step
        self.breakeven_dist = 150     # 15 pips
        self.partial_tp_dist = 250    # 25 pips
        
        # News Filter State
        self.last_news_update = None
        self.cached_news = []
        self.news_buffer_mins = 30  # Pause 30m before/after news
        
        # Indicator Cache
        self.last_indicator_update = None
        self.cached_indicators = {}

        # Database Setup
        self.db_path = "trading_history.db"
        self._init_db()

        # Bot Identification
        self.magic_number = 131313
        self.trade_comment = "Antigravity-AI-Bot"

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                     (ticket INTEGER PRIMARY KEY, symbol TEXT, type TEXT, volume REAL, 
                      price_open REAL, price_close REAL, profit REAL, time_open TEXT, time_close TEXT)''')
        conn.commit()
        conn.close()

    async def get_history(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM trades ORDER BY time_close DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()
        return rows

    async def get_chart_data(self, timeframe=mt5.TIMEFRAME_M15, count=100):
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
        if rates is None: return []
        return [{"time": int(r[0]), "open": r[1], "high": r[2], "low": r[3], "close": r[4]} for r in rates]

    async def initialize(self):
        """Initializes the MetaTrader 5 connection."""
        print(f"Connecting to MT5 Terminal for {self.login}...")
        
        # Combined initialize and login is more reliable on some Windows setups
        if not mt5.initialize(path=self.terminal_path, login=self.login, password=self.password, server=self.server):
            print(f"Failed to connect to MT5 account {self.login}. Error: {mt5.last_error()}")
            return False

        print(f"Connected to MT5 account {self.login}")
        return True

    async def get_market_snapshot(self, symbol="XAUUSDm"):
        """Fetches the latest tick, account info, and multi-timeframe indicators."""
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        
        # Helper to calculate indicators
        def calc_indicators(timeframe, count=100):
            import pandas as pd
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) < 20:
                return {"rsi": 50, "sma": 0, "trend": "NEUTRAL", "price": 0}
            
            df = pd.DataFrame(rates)
            # SMA
            df['sma'] = df['close'].rolling(window=20).mean()
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df['rsi'] = 100 - (100 / (1 + (gain / loss)))
            
            # ATR (14)
            high_low = df['high'] - df['low']
            high_cp = (df['high'] - df['close'].shift()).abs()
            low_cp = (df['low'] - df['close'].shift()).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['atr'] = tr.rolling(window=14).mean()
            
            last_price = df['close'].iloc[-1]
            last_sma = df['sma'].iloc[-1]
            last_rsi = df['rsi'].iloc[-1]
            last_atr = df['atr'].iloc[-1]
            
            return {
                "rsi": round(float(last_rsi), 2),
                "sma": round(float(last_sma), 2),
                "atr": round(float(last_atr), 3),
                "trend": "BULLISH" if last_price > last_sma else "BEARISH",
                "price": last_price
            }

        m15 = calc_indicators(mt5.TIMEFRAME_M15)
        h1 = calc_indicators(mt5.TIMEFRAME_H1)
        d1 = calc_indicators(mt5.TIMEFRAME_D1)

        account_info = mt5.account_info()
        balance = account_info.balance if account_info else 0
        equity = account_info.equity if account_info else 0
        margin = account_info.margin if account_info else 0
        margin_free = account_info.margin_free if account_info else 0
        margin_level = account_info.margin_level if account_info else 0
        
        return {
            "bid": tick.bid,
            "ask": tick.ask,
            "balance": balance,
            "equity": equity,
            "margin": margin,
            "margin_free": margin_free,
            "margin_level": margin_level,
            "m15": m15,
            "h1": h1,
            "d1": d1
        }

    def get_signal(self, snapshot):
        """Calculates signal locally based on Triple Timeframe confluence with Bearish Bias."""
        if not snapshot:
            return "HOLD"

        m15 = snapshot['m15']
        h1 = snapshot['h1']
        d1 = snapshot['d1']

        # print(f"Signal Logic -> D1: {d1['trend']} | H1: {h1['trend']} | M15: {m15['trend']} | RSI: {m15['rsi']}")

        # Strategy: Aggressive Selling in Bearish Daily Trend
        if d1['trend'] == "BEARISH":
            # Condition A: H1 and M15 both align (High Confidence Sell)
            if h1['trend'] == "BEARISH" and m15['trend'] == "BEARISH":
                if m15['rsi'] > 30: # Not Oversold
                    return "SELL"
            
            # Condition B: Sell the Rally (Sensitive)
            # If D1 is bearish, we sell even if H1 is bullish IF RSI is overbought
            if m15['rsi'] > 70:
                print(">>> SENSITIVE SIGNAL: Selling the rally while D1 is Bearish.")
                return "SELL"

        # Strategy: Strict Buying in Bearish Daily Trend (Requires Confluence)
        if d1['trend'] == "BULLISH":
            if h1['trend'] == "BULLISH" and m15['trend'] == "BULLISH":
                if m15['rsi'] < 70: # Not Overbought
                    return "BUY"
            
            # Buy the Dip
            if m15['rsi'] < 30:
                print(">>> SENSITIVE SIGNAL: Buying the dip while D1 is Bullish.")
                return "BUY"

        return "HOLD"

        # EXIT Condition (CRITICAL): Signal Flip
        return "HOLD"

    async def get_open_positions(self):
        """Returns active positions managed by this bot (filtered by magic number)."""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        
        # Filter: Only own trades
        return [p for p in positions if p.magic == self.magic_number]

    async def close_all_positions(self):
        """Closes all active positions for the current symbol."""
        positions = await self.get_open_positions()
        for pos in positions:
            print(f">>> CLOSING POSITION: Ticket #{pos.ticket} ({pos.type})")
            
            # To close a position, we send a counter-order
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "magic": 123456,
                "comment": "AI Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f">>> CLOSE FAILED: Ticket #{pos.ticket}, Code: {result.retcode}")
            else:
                print(f">>> CLOSE SUCCESSFUL: Ticket #{pos.ticket}")
                self.send_telegram(f"✅ POSITION CLOSED: Ticket #{pos.ticket} for Symbol {self.symbol}")

    def is_trading_session(self):
        """Checks if current time is within trading hours."""
        from datetime import datetime
        now = datetime.now().hour
        return self.start_hour <= now <= self.end_hour

    def check_daily_limit(self):
        """Checks if daily loss limit has been hit."""
        account_info = mt5.account_info()
        if not account_info: return True
        
        # Simplified: Check if equity is significantly below balance
        drawdown = (account_info.balance - account_info.equity) / account_info.balance
        if drawdown > self.daily_loss_limit:
            print(f"!!! DAILY LOSS LIMIT HIT ({drawdown*100:.2f}%). SHUTTING DOWN.")
            return False
        return True

    async def _fetch_news(self):
        """Fetches news from Forex Factory JSON feed and caches it."""
        from datetime import datetime
        if self.last_news_update and (datetime.utcnow() - self.last_news_update).seconds < 3600:
            return

        import requests
        try:
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.cached_news = response.json()
                self.last_news_update = datetime.utcnow()
                print(">>> NEWS FEED UPDATED.")
        except Exception as e:
            print(f"News Fetch Error: {e}")

    async def is_news_paused(self):
        """Checks if high-impact USD news is coming or just passed."""
        await self._fetch_news()
        if not self.cached_news:
            return False

        from datetime import datetime, timezone
        import dateutil.parser
        
        # FF Feed uses UTC/GMT
        now = datetime.now(timezone.utc)
        
        for event in self.cached_news:
            # We only care about High Impact USD news for Gold
            if event.get('impact') == 'High' and event.get('country') == 'USD':
                try:
                    event_time = dateutil.parser.isoparse(event.get('date'))
                    # If news is within the 30-minute window (before or after)
                    time_diff = (event_time - now).total_seconds() / 60.0
                    
                    if abs(time_diff) < self.news_buffer_mins:
                        print(f"!!! TRADING PAUSED: High Impact News ({event.get('title')}) in {time_diff:.1f} mins.")
                        return True
                except:
                    continue
        
        return False

    def send_telegram(self, message):
        """Sends a notification to Telegram."""
        if not self.tg_token or not self.tg_chat_id:
            return
        import requests
        try:
            url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
            payload = {"chat_id": self.tg_chat_id, "text": message}
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Telegram Error: {e}")

    def calculate_lot_size(self):
        """Calculates lot size based on equity and risk percent."""
        account_info = mt5.account_info()
        if account_info is None:
            return 0.01
        
        equity = account_info.equity
        # Simple risk model: 0.01 lot per $1000 for each 1% risk
        # For Gold on Exness, 0.01 lot is roughly $1-2 risk per 100 points
        base_lot = (equity / 1000.0) * (self.risk_percent * 100.0) * 0.01
        
        # Ensure minimum lot size
        lot = round(max(0.01, base_lot), 2)
        return lot

    async def update_trailing_stops(self):
        """Updates trailing stops, handles breakeven and partial closes."""
        positions = await self.get_open_positions()
        if not positions:
            return

        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            return

        for pos in positions:
            current_sl = pos.sl
            current_tp = pos.tp
            new_sl = 0
            
            # Point conversion for Gold
            pts = 0.01 

            if pos.type == mt5.POSITION_TYPE_BUY:
                profit_pts = tick.bid - pos.price_open
                
                # 1. Partial Profit Scaling (Close 50% at target)
                # We check if volume is > 0.01 to see if we can still partial
                if profit_pts > self.partial_tp_dist * pts and pos.volume > 0.01:
                    close_vol = round(pos.volume / 2, 2)
                    if close_vol >= 0.01:
                        print(f">>> PARTIAL TP: Closing {close_vol} of Ticket #{pos.ticket}")
                        self.partial_close(pos, close_vol)

                # 2. Auto-Breakeven
                if profit_pts > self.breakeven_dist * pts:
                    be_level = pos.price_open + (10 * pts) # Entry + 1 pip
                    if current_sl < be_level:
                        new_sl = be_level
                        print(f">>> BREAKEVEN: Protecting Ticket #{pos.ticket}")

                # 3. Standard Trailing
                if profit_pts > self.trailing_stop_dist * pts:
                    potential_sl = tick.bid - (self.trailing_stop_dist * pts)
                    if potential_sl > current_sl + (self.trailing_step * pts):
                        new_sl = round(potential_sl, 3)
            
            elif pos.type == mt5.POSITION_TYPE_SELL:
                profit_pts = pos.price_open - tick.ask
                
                # 1. Partial TP
                if profit_pts > self.partial_tp_dist * pts and pos.volume > 0.01:
                    close_vol = round(pos.volume / 2, 2)
                    if close_vol >= 0.01:
                        print(f">>> PARTIAL TP: Closing {close_vol} of Ticket #{pos.ticket}")
                        self.partial_close(pos, close_vol)

                # 2. Auto-Breakeven
                if profit_pts > self.breakeven_dist * pts:
                    be_level = pos.price_open - (10 * pts)
                    if current_sl > be_level or current_sl == 0:
                        new_sl = be_level
                        print(f">>> BREAKEVEN: Protecting Ticket #{pos.ticket}")

                # 3. Standard Trailing
                if profit_pts > self.trailing_stop_dist * pts:
                    potential_sl = tick.ask + (self.trailing_stop_dist * pts)
                    if potential_sl < current_sl - (self.trailing_step * pts) or current_sl == 0:
                        new_sl = round(potential_sl, 3)

            if new_sl > 0:
                self.modify_sl(pos.ticket, new_sl, current_tp)

    def partial_close(self, pos, volume):
        """Closes a specific volume of a position."""
        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(self.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "position": pos.ticket,
            "price": price,
            "magic": self.magic_number,
            "comment": f"{self.trade_comment} (Partial)",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.send_telegram(f"💰 PARTIAL TP: Closed {volume} lots on Ticket #{pos.ticket}")

    def modify_sl(self, ticket, sl, tp):
        """Modifies SL/TP of a position."""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "sl": sl,
            "tp": tp,
            "position": ticket
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f">>> MOD FAILED: {result.comment}")

    async def execute_trade(self, action, volume=None):
        """Executes a market order on MT5."""
        if action not in ["BUY", "SELL"]:
            return

        tick = mt5.symbol_info_tick(self.symbol)
        spread_points = (tick.ask - tick.bid) / 0.01 # Gold conversion
        
        if spread_points > self.max_spread:
            print(f">>> TRADE BLOCKED: Spread too high ({spread_points:.1f} > {self.max_spread})")
            return

        if not self.check_daily_limit():
            return

        if volume is None:
            volume = self.calculate_lot_size()

        order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.symbol).ask if action == "BUY" else mt5.symbol_info_tick(self.symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "magic": self.magic_number,
            "comment": self.trade_comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        print(f">>> SENDING {action} ORDER: {volume} lots @ {price} (Equiy-Based Risk)")
        result = mt5.order_send(request)
        
        if result is None:
            print(">>> CRITICAL ERROR: mt5.order_send returned None. Check terminal connection.")
            return

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f">>> ORDER FAILED! Result Code: {result.retcode}")
            print(f">>> Comment: {result.comment}")
        else:
            print(f">>> ORDER EXECUTED SUCCESSFULLY! Ticket: {result.order}")
            print(f">>> Filled Price: {result.price}, Profit/Balance Impact: Pending")
            self.send_telegram(f"🚀 {action} EXECUTED: {volume} lots @ {result.price}\nSymbol: {self.symbol}")

    async def close(self):
        mt5.shutdown()

if __name__ == "__main__":
    # Test (Standard synchronous wrapper for MT5 testing)
    import asyncio
    trader = GoldTrader()
    asyncio.run(trader.initialize())
