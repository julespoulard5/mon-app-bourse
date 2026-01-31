import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="StockVision IA", layout="wide")
st.title("📈 StockVision IA")

ticker = st.sidebar.text_input("Symbole (ex: AAPL, MC.PA)", "AAPL").upper()

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # --- ZONE ALERTE & IA ---
    price = info.get('currentPrice', 0)
    target_low = info.get('targetLowPrice', 0)
    
    if price <= target_low and target_low != 0:
        st.error(f"🚨 ALERTE : {ticker} est en dessous de sa cible basse ({target_low}$)")
    
    st.subheader("🤖 Analyse de l'IA")
    roe = info.get('returnOnEquity', 0)
    if roe > 0.15:
        st.success(f"L'IA valide la rentabilité : ROE excellent de {roe*100:.1f}%.")
    else:
        st.warning(f"L'IA conseille la prudence : ROE de {roe*100:.1f}% est moyen.")

    # --- METRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prix", f"{price}$")
    col2.metric("PER", f"{info.get('trailingPE', 'N/A')}x")
    col3.metric("EBITDA", f"{info.get('ebitda', 0)/1e9:.1f}Md")
    col4.metric("FCF", f"{info.get('freeCashflow', 0)/1e9:.2f}Md")

    # --- GRAPHIQUE ---
    st.line_chart(stock.history(period="1y")['Close'])
