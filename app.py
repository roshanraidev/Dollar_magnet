import streamlit as st
import pandas as pd
import time
import pandas_ta as ta
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from datetime import datetime
import asyncio
import threading

# 1. Set page config at the very top — BEFORE any Streamlit command
st.set_page_config(page_title="Professor Bot", layout="wide")

# Fix asyncio event loop issue sometimes with Streamlit
if threading.current_thread() is not threading.main_thread():
    asyncio.set_event_loop(asyncio.new_event_loop())

# ----------- Validate Binance API keys -----------
def validate_api_keys(api_key, api_secret):
    try:
        client = Client(api_key, api_secret)
        client.get_account()  # simple test call
        return True, client, None
    except Exception as e:
        return False, None, str(e)
def add_footer():
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: red;  /* red color text */
        text-align: center;
        padding: 10px;
        font-size: 12px;
        opacity: 0.8;
        z-index: 9999;
    }
    </style>
    <div class="footer">
        © Created by @Mr. Professor
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
# ----------- Main bot interface -----------
def main_app(client):

    # Fetch all symbols once
    valid_symbols = [s['symbol'] for s in client.get_exchange_info()['symbols']]

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.api_key = ""
        st.session_state.api_secret = ""
        st.rerun()
    add_footer()
    # Sidebar controls
    default_symbol = "BTCUSDT" if "BTCUSDT" in valid_symbols else valid_symbols[0]
    symbol = st.sidebar.selectbox("Trading Pair", valid_symbols, index=valid_symbols.index(default_symbol))
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "4h", "1d"])

    # Fetch balance
    available_balance = 0.0
    try:
        balance_resp = client.get_asset_balance(asset='USDT')
        if balance_resp:
            available_balance = float(balance_resp['free'])
    except Exception as e:
        st.error(f"Error fetching balance: {e}")

    if available_balance < 1:
        st.sidebar.warning("⚠️ You need at least 1 USDT to trade.")

    initial_capital = st.sidebar.number_input(
        "Initial Capital (USD)",
        min_value=1.0,
        max_value=available_balance if available_balance > 1 else 1.0,
        value=available_balance if available_balance > 1 else 1.0,        step=1.0
    )

    run_trading = st.sidebar.checkbox("Run Auto Trading")
    st.sidebar.caption("24/7 Bot")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Live Trading Settings")
    st.session_state.real_mode = st.sidebar.checkbox("✅ Enable Real Trading Mode")
    if st.session_state.real_mode:
        st.sidebar.warning("⚠️ Real trading enabled. Use with caution!")

    if initial_capital > available_balance:
        st.warning("Initial capital cannot be more than available balance. Adjust it.")
        run_trading = False

    # Initialize session state variables
    if "positions" not in st.session_state:
        st.session_state.positions = []
    if "pnl" not in st.session_state:
        st.session_state.pnl = 0.0
    if "open_trade" not in st.session_state:
        st.session_state.open_trade = None

    # Fetch klines data
    def fetch_data(symbol, interval):
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=150)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return None

        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.astype({'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'float'})
        return df

    # Add indicators
    def add_indicators(df):
        df['rsi'] = ta.rsi(df['close'], length=14)
        macd = ta.macd(df['close'])
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        return df

    # Get min notional filter
    def get_min_notional(symbol):
        try:
            info = client.get_symbol_info(symbol)
            for f in info['filters']:
                if f['filterType'] == 'MIN_NOTIONAL':
                    return float(f['minNotional'])
        except:
            pass
        return 1.0

    # Place order logic
    def place_order(side, qty, price):
        now = datetime.now()
        trade_mode = st.session_state.get("real_mode", False)
        qty = float(f"{qty:.6f}")

        if side == SIDE_SELL and st.session_state.open_trade:
            entry = st.session_state.open_trade
            pnl = (price - entry['price']) * qty
            st.session_state.pnl += pnl
            if trade_mode:
                try:
                    client.order_market_sell(symbol=symbol, quantity=qty)
                    st.success(f"✅ Real SELL order placed at ${price:.2f}")
                except Exception as e:
                    st.error(f"Error placing SELL order: {e}")
            st.session_state.open_trade = None
            st.session_state.positions.append({"time": now, "action": "SELL", "price": price, "qty": qty, "pnl": pnl})

        elif side == SIDE_BUY:
            st.session_state.open_trade = {"price": price, "qty": qty, "time": now}
            if trade_mode:
                try:
                    client.order_market_buy(symbol=symbol, quantity=qty)
                    st.success(f"✅ Real BUY order placed at ${price:.2f}")
                except Exception as e:
                    st.error(f"Error placing BUY order: {e}")
            st.session_state.positions.append({"time": now, "action": "BUY", "price": price, "qty": qty, "pnl": None})

    # Trading strategy logic
    def trading_strategy(df, capital):
        min_notional = get_min_notional(symbol)
        price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        macd = df['macd'].iloc[-1]
        signal = df['macd_signal'].iloc[-1]

        if st.session_state.open_trade:
            entry = st.session_state.open_trade
            unrealized_pct = (price - entry['price']) / entry['price'] * 100

            if unrealized_pct <= -15:
                place_order(SIDE_SELL, entry['qty'], price)
                st.warning(f"STOP LOSS triggered: {unrealized_pct:.2f}%")
                return

            if 20 <= unrealized_pct < 30:
                if macd < signal:
                    place_order(SIDE_SELL, entry['qty'], price)
                    st.success("Take Profit at 20% - MACD bearish")
                    return

            if unrealized_pct >= 30:
                if macd < signal:
                    place_order(SIDE_SELL, entry['qty'], price)
                    st.success("Exit at >30% profit - MACD bearish")
                    return
        else:
            qty = capital / price
            if qty * price >= min_notional:
                if rsi < 30 and macd > signal:
                    place_order(SIDE_BUY, qty, price)
                    st.success("BUY signal triggered")

    # Plot charts
    def plot_chart(df):
        fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        axs[0].plot(df.index, df['close'], label='Close Price', color='black')
        axs[0].legend()
        axs[1].plot(df.index, df['rsi'], label='RSI', color='blue')
        axs[1].axhline(70, color='red', linestyle='--')
        axs[1].axhline(30, color='green', linestyle='--')
        axs[1].legend()
        axs[2].plot(df.index, df['macd'], label='MACD', color='purple')
        axs[2].plot(df.index, df['macd_signal'], label='Signal', color='orange')
        axs[2].legend()
        st.pyplot(fig)

    if symbol not in valid_symbols:
        st.error("Invalid trading symbol selected.")
        return

    df = fetch_data(symbol, interval)
    if df is None:
        return

    df = add_indicators(df)

    current_price = df['close'].iloc[-1]
    rsi_now = df['rsi'].iloc[-1]
    capital = initial_capital + st.session_state.pnl

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capital", f"${capital:,.2f}")
    col2.metric("Price", f"${current_price:.2f}")
    col3.metric("Unrealized PnL", f"${st.session_state.pnl:.2f}")
    col4.metric("RSI", f"{rsi_now:.2f}")

    if run_trading:
        trading_strategy(df, capital)

    plot_chart(df)

    if st.session_state.positions:
        st.subheader("Trade Log")
        df_pos = pd.DataFrame(st.session_state.positions)
        st.dataframe(df_pos)
        st.download_button("Download CSV", df_pos.to_csv(index=False), file_name=f"trade_log_{symbol}.csv")

    st.caption("Auto-refresh every 60 seconds")
    if run_trading:
        time.sleep(60)
        st.rerun()

# ----------- APP ENTRY POINT -----------
def app():
    st.title("🔐 Mr Professor Bot")

    if st.session_state.get("logged_in", False):
        client = Client(st.session_state.api_key, st.session_state.api_secret)
        main_app(client)
    else:
        with st.form("login_form"):
            api_key = st.text_input("API Key", type="password")
            api_secret = st.text_input("API Secret", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if not api_key or not api_secret:
                    st.error("Please enter both API Key and Secret.")
                else:
                    valid, client, error = validate_api_keys(api_key, api_secret)
                    if valid:
                        st.session_state.api_key = api_key
                        st.session_state.api_secret = api_secret
                        st.session_state.logged_in = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Sorry login failed,enter correct api and secret key for excess")

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.api_key = ""
        st.session_state.api_secret = ""

    app()
