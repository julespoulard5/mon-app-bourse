import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration
st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision : Edition Trade Republic")

# Recherche
with st.form("search_form"):
    col_search, col_button = st.columns([4, 1])
    with col_search:
        ticker_input = st.text_input("Symbole (ex: AAPL, MC.PA, TSLA)", value="AAPL").upper()
    with col_button:
        submitted = st.form_submit_button("Analyser")

st.markdown("---")

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        if info and 'currentPrice' in info:
            prix_brut = info.get('currentPrice')
            devise_org = info.get('currency', 'USD')
            nom = info.get('longName', ticker_input)

            # Conversion Euro
            taux = 1.0
            if devise_org != "EUR":
                try:
                    taux = yf.Ticker(f"{devise_org}EUR=X").info.get('regularMarketPrice', 1)
                except:
                    taux = 0.92 # Valeur par défaut si l'API de conversion flanche
            
            prix_eur = prix_brut * taux

            st.header(f"📊 {nom}")
            st.metric("Prix Estimé", f"{prix_eur:.2f} €")

            # Indicateurs
            st.subheader("🤖 Indicateurs Clés")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PER", f"{info.get('trailingPE', 'N/A')}x")
            m2.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
            m3.metric("EBE (EBITDA)", f"{info.get('ebitda', 0)/1e9:.2f} Md")
            m4.metric("Cash-Flow", f"{info.get('freeCashflow', 0)/1e9:.2f} Md")

            # Graphique
            st.subheader("📈 Évolution du cours (1 an)")
            hist = stock.history(period="1y")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Prix (€)", line=dict(color='#00ff00')))
            fig.update_layout(xaxis_title="Date", yaxis_title="Prix en Euros", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # Actualités sécurisées
            st.divider()
            st.subheader("📰 Actualités")
            news = stock.news
            if news:
                for n in news[:3]:
                    st.write(f"🔹 **[{n.get('title', 'Titre non dispo')}]({n.get('link', '#')})**")
            else:
                st.write("Aucune news trouvée.")

        else:
            st.warning("Action non trouvée. Vérifiez le symbole.")
    except Exception as e:
        st.error(f"Erreur d'analyse : {e}")


