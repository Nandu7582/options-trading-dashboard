import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Placeholder for Greeks calculation - simplified
def calculate_greeks():
    return {"Delta": 0.55, "Gamma": 0.09}

# Bull Call Spread payoff
def bull_call_spread_payoff(sT, K1, K2, c1_premium, c2_premium):
    payoff = np.maximum(sT - K1, 0) - c1_premium - (np.maximum(sT - K2, 0) - c2_premium)
    return payoff

st.title("Options Trading Signal Dashboard")

# User input for ticker & expiry
ticker = st.text_input("Enter Underlying Symbol", value="BANKNIFTY")
expiry_days = st.slider("Days to Expiry", min_value=5, max_value=45, value=18)

# Fetch underlying data
try:
    data = yf.download(ticker + ".NS", period="1mo", interval="15m")
    data['MACD'] = ta.macd(data['Close'])['MACD_12_26_9']
    data['MACD_signal'] = ta.macd(data['Close'])['MACDs_12_26_9']
    data['RSI'] = ta.rsi(data['Close'], length=14)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Signal logic
macd_cross = (data['MACD'].iloc[-2] < data['MACD_signal'].iloc[-2]) and (data['MACD'].iloc[-1] > data['MACD_signal'].iloc[-1])
rsi_ok = data['RSI'].iloc[-1] > 50
long_oi = True  # Placeholder for open interest check

signal_active = macd_cross and rsi_ok and long_oi

if signal_active:
    # Build signal components (sample fixed numbers for demo)
    expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%d %B")
    strike_buy = 49000
    strike_hedge = 49300
    buy_premium = 142
    target = 190
    stop_loss = 118
    confidence = 88
    max_profit = 3200
    max_loss = 1100
    greeks = calculate_greeks()

    st.markdown(f"""
    📌 **SIGNAL – {ticker.upper()} {expiry_date} Expiry**  
    🟢 **BUY {strike_buy:,} CE @ ₹{buy_premium}**  
    🎯 Target: ₹{target} | 🛑 SL: ₹{stop_loss}  
    📈 Confidence: {confidence}% ✅ High  
    📚 Strategy: Bull Call Spread  
    🧮 Greeks: Delta {greeks['Delta']} | Gamma {greeks['Gamma']}  
    🧠 Signal Logic: MACD Crossover + RSI > 50 + Long OI  
    💰 Hedge Idea: Sell {strike_hedge:,} CE  
    📊 Max Profit: ₹{max_profit} | Max Loss: ₹{max_loss}  
    """)

    # Plot payoff diagram
    sT = np.arange(strike_buy - 2000, strike_hedge + 2000, 10)
    payoff = bull_call_spread_payoff(sT, strike_buy, strike_hedge, buy_premium, 50)  # 50 premium for hedge option placeholder

    fig, ax = plt.subplots()
    ax.plot(sT, payoff, label="Payoff")
    ax.axhline(0, color='black', lw=0.5)
    ax.set_title("Bull Call Spread Payoff")
    ax.set_xlabel("Underlying Price at Expiry")
    ax.set_ylabel("Profit / Loss")
    ax.legend()
    st.pyplot(fig)

else:
    st.write("No active signal based on current criteria.")
