# Dollar_magnet (Professor Bot)

A crypto trading bot dashboard built with Streamlit for Binance users. Analyze, simulate, and automate your crypto trading with transparent strategies and risk management tools.

## Features

- Secure Binance API login (your keys aren't stored long-term)
- Interactive dashboard for prices, technical indicators, and trade history
- Technical indicators (RSI,MACD) 
- Simulated or live trading (enable "Real Trading Mode" for actual orders)
- Risk management: stop loss, take profit
- Downloadable trading logs
- Auto trading with 60-second refresh

## How It Works

1. **Login:** Enter your Binance API key and secret to authenticate.
2. **Dashboard Controls:** 
   - Choose a trading pair (e.g., BTCUSDT)
   - Select chart interval (1m, 5m, 15m, etc.)
   - Set your trading capital and enable/disable auto or real trading
3. **Strategy:**
   - **Buy:** If RSI < 30 and MACD is bullish
   - **Sell:** If loss > 15% (stop loss), or profit 20-30% and MACD bearish (take profit), or profit > 30% and MACD bearish
4. **Visualization:** View price, RSI, MACD charts, and your trade log (downloadable as CSV)
5. **Automation:** Auto-trading mode checks and trades every minute

## Getting Started

1. Install requirements:
2. Run the app:
3. Open the web browser to the link shown in the terminal.
4. Enter your Binance API key and secret.
5. Set preferences in the sidebar and optionally enable auto/real trading.

## Notes

- **Risk:** Enabling "Real Trading Mode" will place real trades on your Binance account. Use with caution!
- **Security:** Never share your API keys. Only use your own keys and keep them safe.
- **Educational Purpose:** This bot is for educational purposes and demonstration only.

---

© Created by @Mr. Professor
