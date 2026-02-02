# Gemini AI Integration Instructions

This bot uses **Google Gemini** as the brain for trading decisions. Instead of a standard API key, it is designed to use your existing Google Account login via the `gemini-cli`.

## Why `gemini-cli`?
- **No API Limits**: Uses your personal account session.
- **Easy Setup**: No need to manage secrets or billing in Google Cloud Console.
- **Privacy**: Leverages your existing authenticated environment.

## Integration Workflow
The `ai_analyst.py` module performs the following:
1. Formats a structured prompt containing current price, bid/ask, and technical indicators.
2. Calls the system command `/opt/homebrew/bin/gemini` (or `gemini` on Windows).
3. Parses the output to extract `RECOMMENDATION` (BUY/SELL/HOLD).

## Prompt Engineering
The current prompt template used:
```text
Analyze the following market data and technical indicators to provide a trading recommendation (BUY, SELL, or HOLD).

Market Data: {market_data}
Technical Indicators: {technical_indicators}

Response format:
REASONING: <brief reasoning>
RECOMMENDATION: <BUY|SELL|HOLD>
CONFIDENCE: <0-100%>
```

## Customization
To improve accuracy, you can modify `ai_analyst.py` to include:
- Historical candle data (H1/M15/M5).
- Global news sentiment.
- Specific candlestick pattern detection logic.
