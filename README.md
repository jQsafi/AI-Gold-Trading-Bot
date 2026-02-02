# AI-Assisted Gold Trading Bot (XAUUSD)

This repository contains a professional AI trading bot designed for the Gold (XAUUSD) market on **Exness**. It leverages **Google Gemini** (via `gemini-cli`) for market analysis and the **Native MetaTrader 5 (MT5)** library for trade execution on Windows.

## 🚀 Overview
- **AI Analyst**: Uses Gemini to analyze price action, trends, and momentum.
- **Native Execution**: Connects directly to the MT5 terminal on Windows for low-latency trading.
- **Zero-Cost Connectivity**: No need for expensive cloud APIs (like MetaAPI) when running on Windows.

## 🛠 Prerequisites
1. **Windows OS**: The `MetaTrader5` Python library is Windows-only.
2. **Exness MT5 Terminal**: Installed and logged into your account.
3. **Python 3.10+**: Installed on your system.
4. **Gemini CLI**: Installed and authenticated on your machine.
   - Install via: `npm install -g @google/gemini-cli`
   - Authenticate: `gemini login`

## ⚙️ Configuration
1. Rename `.env.example` to `.env`.
2. Enter your Exness MT5 credentials:
   ```env
   MT5_LOGIN=your_login_here
   MT5_PASSWORD=your_password_here
   MT5_SERVER=your_server_here (e.g., Exness-MT5Trial6)
   ```

## 🏃‍♂️ How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the bot:
   ```bash
   python main.py
   ```

## 📂 Project Structure
- `main.py`: The orchestrator managing the trading cycle.
- `ai_analyst.py`: Bridges the bot to Gemini for intelligence.
- `trader.py`: Native MT5 execution logic.
- `requirements.txt`: Python package dependencies.
- `Gemini.md`: Specific instructions for AI integration.

## ⚠️ Disclaimer
Trading involves significant risk. This bot is for educational purposes. Always test on a Demo account before considering live markets.
