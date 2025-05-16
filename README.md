This project is a crypto trading bot dashboard built with Streamlit that connects to your Binance account and helps you trade cryptocurrencies automatically using a simple trading strategy. Below is an explanation for new users about what the project does and how the script works.

What is this project about?

Purpose:
This project is a web-based application called "Professor Bot" that lets you connect your Binance account, view your balance, analyze crypto market data, and (optionally) run an automated trading bot using technical indicators like RSI and MACD.
Features:
Secure Binance API login (your keys are not stored long-term).
Visual dashboard for prices, indicators, and your bot’s trades.
Simulated or live trading (enable real trading mode if you want actual orders placed).
Basic risk management (stop loss, take profit).
Downloadable trading logs.
How does the script work?

1. App Initialization

The app uses Streamlit, so it creates a web dashboard.
It asks you to enter your Binance API Key and Secret (these are required to access your account data and place trades).
2. Login & Validation

When you log in, the script checks if your API credentials are valid by making a simple Binance API call.
If successful, you’ll see the main dashboard; otherwise, you get an error.
3. Main Trading Dashboard

Sidebar Controls:
Select the trading pair (like BTCUSDT).
Select the chart interval (1 minute, 5 minutes, etc.).
See your available USDT balance.
Choose how much capital to allocate for trading.
Toggle "Run Auto Trading" and "Enable Real Trading Mode".
If “Real Trading” is off, the bot only simulates trades.
If on, the bot can place real market orders!
Metrics:
Shows your trading capital, current price, unrealized profit/loss, and RSI indicator value.
4. Fetching Data from Binance

The app fetches historical price (“candle” or “kline”) data for the selected symbol and interval.
5. Technical Indicators

Calculates RSI (Relative Strength Index) and MACD (Moving Average Convergence Divergence) using the pandas_ta library.
6. Trading Logic (Strategy)

The script checks if you’re in a trade or not.
Entry (Buy):
Buys if RSI is below 30 (oversold) and MACD is bullish.
Buys enough amount to not violate Binance’s minimum notional rule.
Exit (Sell):
Sells if:
Loss is more than 15% (stop loss).
Profit is 20-30% and MACD turns bearish (take profit).
Profit is over 30% and MACD turns bearish (strong take profit).
All trades and their outcomes are logged.
7. Visualization

Displays line charts for price, RSI, and MACD using matplotlib.
Shows your trade log in a table, with an option to download as CSV.
8. Auto-refresh

If auto trading is enabled, the page refreshes every 60 seconds to fetch new data and re-evaluate trades.
How to Use

Install requirements (Streamlit, pandas, pandas_ta, matplotlib, python-binance).
Run the app:
Code
streamlit run app.py
Open the web browser to the link shown in the terminal.
Enter your Binance API key and secret.
Set your preferences in the sidebar, and optionally enable auto trading and real trading mode.
Important Notes

Risk: Enabling "Real Trading Mode" will place real trades on your Binance account. Use with caution!
Security: Never share your API keys with anyone. Only use with your own keys and keep them safe.
Educational purpose: This bot is a simple example and not meant for serious trading without understanding the risks.
