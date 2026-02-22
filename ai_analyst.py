import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        # We assume 'gemini' is in the path or provided by the environment
        self.cli_path = "gemini"

    def analyze_market(self, market_data, indicators, news_context=""):
        """
        Analyzes market data, indicators, and news using gemini-cli.
        """
        prompt = f"""
        Your objective: Technical + Fundamental Analysis for Gold.

        Snapshot: {market_data}
        Technicals: {indicators}
        News: {news_context}

        Rules:
        - If H1+M15 Trend align and News is same = HIGH CONFIDENCE.
        - RECOMMENDATION: BUY/SELL/HOLD/CLOSE. 
        - CRITICAL_SITUATION: YES if trend breaks.

        Format:
        CRITICAL_SITUATION: <YES/NO>
        REASONING: <Concise>
        RECOMMENDATION: <BUY|SELL|HOLD|CLOSE>
        CONFIDENCE: <0-100%>
        """
        
        # Strip multiline whitespace to avoid shell issues
        clean_prompt = "\n".join([line.strip() for line in prompt.split("\n") if line.strip()])
        
        print("-" * 50)
        print(">>> SENDING PROMPT TO GEMINI...")
        print("-" * 50)
        
        try:
            # Call the gemini-cli as a one-shot command using the -p flag
            result = subprocess.run(
                [self.cli_path, "-p", clean_prompt],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            print(">>> RAW AI RESPONSE RECEIVED.")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f">>> CLI ERROR: {e.stderr}")
            return f"Error calling gemini-cli: {e.stderr}"
        except Exception as e:
            print(f">>> UNEXPECTED ERROR: {str(e)}")
            return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Test simulation
    analyst = AIAnalyst()
    sample_data = "Price: 2045.50, Change: +0.2%"
    sample_indicators = "RSI: 65, MACD: Bullish Crossover"
    print(analyst.analyze_market(sample_data, sample_indicators))
