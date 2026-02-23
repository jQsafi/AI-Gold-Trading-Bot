import asyncio
import os
import MetaTrader5 as mt5
from dotenv import load_dotenv
from trader import GoldTrader
import json
import datetime

load_dotenv()

async def main():
    print("Starting Native MT5 Gold Trading Bot (No AI)...")
    
    # Initialize component
    trader = GoldTrader()
    
    # Connect to Exness via MT5 Native Library
    if not await trader.initialize():
        print("Finalizing due to MT5 connection failure.")
        return

    # Main Bot Loop
    try:
        print("\n" + "="*50)
        print("BOT LIVE: TECHNICAL ANALYSIS MODE (100ms REALTIME)")
        print(f"Trading Symbol: {trader.symbol}")
        print(f"Risk Percent: {trader.risk_percent*100}%")
        print("="*50 + "\n")
        
        last_print_time = datetime.datetime.now()
        print("Entering main loop...")
        
        while True:
            now = datetime.datetime.now()
            should_print = (now - last_print_time).total_seconds() >= 5

            # 1. Fetch live technicals
            snapshot = await trader.get_market_snapshot(trader.symbol)
            if not snapshot:
                await asyncio.sleep(0.1)
                continue
                
            # 2. Check current open positions
            open_positions = await trader.get_open_positions()
            
            # 3. Calculate local signal
            current_signal = trader.get_signal(snapshot)
            
            if should_print:
                print(f"[{now.strftime('%H:%M:%S')}] Price: {snapshot['bid']}/{snapshot['ask']} | Signal: {current_signal} | Open: {len(open_positions)}")
                last_print_time = now

            # Logic Pillar 1: Exit/Flip Logic
            for pos in open_positions:
                pos_type_str = "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL"
                if current_signal != "HOLD" and pos_type_str != current_signal:
                    print(f">>> REALTIME SIGNAL FLIP ({pos_type_str} -> {current_signal}). Closing Ticket #{pos.ticket}.")
                    await trader.close_all_positions()
                    break

            # Logic Pillar 2: Entry Logic
            if len(await trader.get_open_positions()) == 0:
                if trader.is_trading_session():
                    if not await trader.is_news_paused():
                        if current_signal in ["BUY", "SELL"]:
                            print(f">>> REALTIME ENTRY: Executing {current_signal} trade.")
                            await trader.execute_trade(current_signal)
            
            # Logic Pillar 3: Trailing Stop & Management (Realtime)
            await trader.update_trailing_stops()

            # 4. Save State for UI
            history = await trader.get_history()
            chart_data = await trader.get_chart_data()
            
            # Simple "Possibility" calculation based on confluence
            conf = 0
            if snapshot['d1']['trend'] == current_signal: conf += 40
            if snapshot['h1']['trend'] == current_signal: conf += 30
            if snapshot['m15']['trend'] == current_signal: conf += 20
            if abs(snapshot['m15']['rsi'] - 50) > 10: conf += 10
            
            state = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "price": f"{snapshot['bid']}/{snapshot['ask']}",
                "signal": current_signal,
                "signal_prob": conf if current_signal != "HOLD" else 0,
                "open_count": len(open_positions),
                "d1_trend": snapshot['d1']['trend'],
                "h1_trend": snapshot['h1']['trend'],
                "m15_trend": snapshot['m15']['trend'],
                "rsi": snapshot['m15']['rsi'],
                "h1_rsi": snapshot['h1']['rsi'],
                "d1_sma": snapshot['d1']['sma'],
                "h1_sma": snapshot['h1']['sma'],
                "m15_sma": snapshot['m15']['sma'],
                "atr": snapshot['h1']['atr'],
                "balance": snapshot['balance'],
                "equity": snapshot['equity'],
                "margin_free": snapshot['margin_free'],
                "margin_level": snapshot['margin_level'],
                "login": snapshot['login'],
                "name": snapshot['name'],
                "news_paused": await trader.is_news_paused(),
                "positions": [
                    {
                        "ticket": p.ticket,
                        "type": "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
                        "volume": p.volume,
                        "profit": p.profit,
                        "price_open": p.price_open
                    } for p in open_positions
                ],
                "history": history,
                "chart": chart_data
            }
            import os
            # Atomic write to prevent JSONDecodeError race condition in dashboard
            tmp_file = "dashboard_state_tmp.json"
            target_file = "dashboard_state.json"
            with open(tmp_file, "w") as f:
                json.dump(state, f)
            
            try:
                os.replace(tmp_file, target_file)
            except PermissionError:
                # Flask server might hold a read-lock for a few milliseconds
                pass

            # High Frequency Wait (100ms)
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("Bot stopped by user.")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
