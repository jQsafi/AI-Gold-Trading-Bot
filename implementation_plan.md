# Implementation Plan: AI-Assisted Gold Trading Bot (Exness MT5)

This plan outlines the development of an AI-powered trading bot for the Gold (XAUUSD) market on Exness, utilizing **Antigravity** for orchestration and **Gemini** for market analysis.

## 1. Architecture Overview
- **Core Engine:** Python-based bot that manages data fetching, AI analysis, and trade execution.
- **AI Analyst:** Uses Google Gemini (via `gemini-cli`) to analyze price action. This allows utilizing your existing Google Account login without needing a separate API key.
- **Trading Connectivity:** 
    - **MetaAPI (Cloud MT5):** Used to connect to Exness. This is the most reliable way to trade on MT5 from macOS.

## 2. Tech Stack
- **Language:** Python 3.x
- **AI Integration:** `google-generativeai` SDK (better for programmatic integration than calling the CLI binary).
- **Trading API:** MetaAPI (MetaTrader 4/5 Cloud API).
- **Data Analysis:** Pandas, TA-Lib (or similar) for technical indicators.

## 3. Features
- **Real-time Monitoring:** Fetching live XAUUSD prices.
- **AI Decision Making:** Sending technical snapshots to Gemini for trade suggestions (Buy/Sell/Hold).
- **Automated Execution:** Placing orders with Stop Loss (SL) and Take Profit (TP).
- **Risk Management:** Calculating lot sizes based on account balance and risk percentage.
- **Reporting:** Logging trades and AI reasoning.

## 4. Proposed File Structure
- `main.py`: Entry point for the bot.
- `ai_analyst.py`: Handles interaction with Gemini.
- `trader.py`: Handles MT5/Exness execution logic.
- `config.py`: Configuration for API keys and account details.
- `requirements.txt`: Project dependencies.

## 5. Next Steps
1. **Initialize Project:** Create the directory structure and virtual environment.
2. **Setup Gemini:** Obtain API key and verify connection.
3. **Setup Trading Account:** Configure Exness MT5 account details.
4. **Develop Prototype:** Implement a basic "Read Data -> AI Analysis -> Log Signal" loop.

**Would you like me to proceed with Option A (MetaAPI) or do you have another preference for connecting to Exness on Mac?**
