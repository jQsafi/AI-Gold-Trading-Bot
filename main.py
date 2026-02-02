import asyncio
import os
from dotenv import load_dotenv
from ai_analyst import AIAnalyst
from trader import GoldTrader

load_dotenv()

async def main():
    print("Starting AI Gold Trading Bot...")
    
    # Initialize components
    analyst = AIAnalyst()
    trader = GoldTrader()
    
    # Connect to Exness via MT5 Native Library
    if not await trader.initialize():
        print("Finalizing due to MT5 connection failure.")
        return
    
    # Main Bot Loop
    try:
        while True:
            # 1. Fetch live data
            print("\nFetching market snapshot...")
            snapshot = await trader.get_market_snapshot("XAUUSD")
            print(f"Data: {snapshot}")
            
            # 2. Analyze with Gemini CLI
            print("Analyzing with Gemini AI...")
            technical_indicators = "RSI: (Fetch from MT5), MA: (Fetch from MT5)"
            analysis = analyst.analyze_market(snapshot, technical_indicators)
            print(f"AI Response:\n{analysis}")
            
            # 3. Extract Recommendation
            if "RECOMMENDATION: BUY" in analysis.upper():
                await trader.execute_trade("BUY")
            elif "RECOMMENDATION: SELL" in analysis.upper():
                await trader.execute_trade("SELL")
            
            # Wait for next cycle (5 minutes)
            await asyncio.sleep(300)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
