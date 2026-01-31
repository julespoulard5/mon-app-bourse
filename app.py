import streamlit as st
import yfinance as yf
import pandas as pd

# Configuration de l'interface
st.set_page_config(page_title="StockVision IA", layout="wide")
st.title("📈 StockVision IA : Analyse Boursière")

# Barre latérale pour choisir l'action
ticker = st.sidebar.text_input("Entrez un symbole (ex: AAPL, MC.PA, TSLA)", "AAPL").upper()

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # --- ANALYSE IA ET ALERTES ---
    price = info.get('currentPrice', 0)
    target_low = info.get('targetLowPrice', 0)
    
    if target_low and price <= target_low:
        st.error(f"🚨 ALERTE SOLDE : Le prix ({price}$) est inférieur à la cible basse ({target_low}$)")
    else:
        st.success(f"✅ Prix actuel : {price}$ (Au-dessus du support analyste)")

    st.subheader("🤖 Diagnostic de l'Intelligence Artificielle")
    roe = info.get('returnOnEquity', 0)
    if roe > 0.15:
        st.info(f"Analyse IA : Entreprise très performante. Le rendement (ROE) de {roe*100:.1f}% est un signal d'achat solide.")
    else:
        st.warning(f"Analyse IA : Prudence recommandée. La rentabilité est de {roe*100:.1f}%.")

    # --- INDICATEURS ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PER", f"{info.get('trailingPE', 'N/A')}x")
    c2.metric("EBITDA", f"{info.get('ebitda', 0)/1e9:.1f} Md")
    c3.metric("Free Cash Flow", f"{info.get('freeCashflow', 0)/1e9:.1f} Md")
    c4.metric("Cible Moyenne", f"{info.get('targetMeanPrice', 'N/A')}$")

    # --- HISTORIQUE ---
    st.subheader(f"Évolution de {ticker} sur 1 an")
    hist = stock.history(period="1y")
    st.line_chart(hist['Close'])

    # --- DESCRIPTION ---
    with st.expander("Voir l'histoire de l'entreprise"):
        st.write(info.get('longBusinessSummary', "Pas de description disponible."))

