import streamlit as st
import yfinance as yf
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="StockVision - Trade Republic", layout="wide")

# --- BARRE DE RECHERCHE EN HAUT ---
st.title("🚀 StockVision IA")
ticker_input = st.text_input("🔍 Recherchez une action (ex: AAPL, TSLA, MC.PA)", "AAPL").upper()

st.markdown("---")

if ticker_input:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    
    if 'currentPrice' in info:
        # --- EN-TÊTE ---
        nom = info.get('longName', ticker_input)
        prix = info.get('currentPrice')
        devise = info.get('currency', 'EUR')
        
        col_titre, col_prix = st.columns([3, 1])
        with col_titre:
            st.header(f"{nom}")
        with col_prix:
            st.metric("Prix actuel", f"{prix} {devise}")

        # --- CALCULATEUR D'INVESTISSEMENT ---
        with st.expander("💰 Calculateur Trade Republic"):
            budget = st.number_input("Montant à investir (€)", min_value=0, value=1000)
            nb_actions = budget / prix
            st.write(f"Avec **{budget} €**, vous pouvez acheter environ **{nb_actions:.2f}** actions.")
            
            cible = info.get('targetMeanPrice')
            if cible:
                profit = (cible - prix) * nb_actions
                st.write(f"📈 Si l'objectif de **{cible} {devise}** est atteint, votre profit serait de : **{profit:.2f} €**")

        # --- DIAGNOSTIC IA ---
        st.subheader("🤖 Analyse de l'IA")
        roe = info.get('returnOnEquity', 0)
        per = info.get('trailingPE', 0)
        
        c1, c2 = st.columns(2)
        with c1:
            if roe > 0.15:
                st.success(f"Rentabilité (ROE) : {roe*100:.1f}% - Excellent")
            else:
                st.warning(f"Rentabilité (ROE) : {roe*100:.1f}% - Moyen")
        with c2:
            if per < 20 and per > 0:
                st.success(f"Valorisation (PER) : {per:.1f}x - Attrayant")
            else:
                st.info(f"Valorisation (PER) : {per:.1f}x - Standard")

        # --- STATS TEMPS RÉEL ---
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("EBITDA (EBE)", f"{info.get('ebitda', 0)/1e9:.2f} Md")
        m2.metric("Free Cash Flow", f"{info.get('freeCashflow', 0)/1e9:.2f} Md")
        m3.metric("Dette/Capitaux", f"{info.get('debtToEquity', 'N/A')}")
        m4.metric("Cible Basse", f"{info.get('targetLowPrice', 'N/A')} {devise}")

        # --- GRAPHIQUE ---
        st.subheader("📊 Graphique 1 an")
        hist = stock.history(period="1y")
        st.line_chart(hist['Close'])
        
        # --- NEWS ---
        st.divider()
        st.subheader("📰 Dernières Actualités")
        for n in stock.news[:3]:
            st.write(f"**[{n['title']}]({n['link']})**")

    else:
        st.error("Action non trouvée. Vérifiez le symbole (ex: AIR.PA pour Airbus).")
