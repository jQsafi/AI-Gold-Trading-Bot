import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        # We assume 'gemini' is in the path or user provides it
        self.cli_path = "/opt/homebrew/bin/gemini"

    def analyze_market(self, market_data, technical_indicators):
        """
        Analyzes market data using gemini-cli and returns a trading recommendation.
        """
        prompt = f"""
        You are an expert Gold (XAUUSD) trading analyst. 
        Analyze the following market data and technical indicators to provide a trading recommendation (BUY, SELL, or HOLD).
        
        Market Data:
        {market_data}
        
        Technical Indicators:
        {technical_indicators}
        
        Response format:
        REASONING: <your brief reasoning>
        RECOMMENDATION: <BUY|SELL|HOLD>
        CONFIDENCE: <0-100%>
        """
        
        try:
            # Call the gemini-cli
            result = subprocess.run(
                [self.cli_path, prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error calling gemini-cli: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Test simulation
    analyst = AIAnalyst()
    sample_data = "Price: 2045.50, Change: +0.2%"
    sample_indicators = "RSI: 65, MACD: Bullish Crossover"
    print(analyst.analyze_market(sample_data, sample_indicators))
