import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision Pro")

# --- 1. RECHERCHE ÉPURÉE ---
user_query = st.text_input("🔍 Recherchez une action (ex: Apple, LVMH, Nvidia...)", value="").strip()

# Aide à la recherche pour les actions courantes
MAPPING = {
    "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "MICROSOFT": "MSFT",
    "GOOGLE": "GOOGL", "AMAZON": "AMZN", "LVMH": "MC.PA", "HERMES": "RMS.PA",
    "AIRBUS": "AIR.PA", "TOTAL": "TTE.PA", "RENAULT": "RNO.PA"
}

ticker_final = None
if user_query:
    match = [nom for nom in MAPPING.keys() if user_query.upper() in nom]
    if match:
        choix = st.radio("C'est l'une de ces entreprises ?", match, horizontal=True)
        ticker_final = MAPPING[choix]
    else:
        ticker_final = user_query.upper()

st.markdown("---")

if ticker_final:
    try:
        stock = yf.Ticker(ticker_final)
        info = stock.info
        nom = info.get('longName', ticker_final)
        
        # --- HEADER PRIX ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.header(f"📊 {nom}")
        with c2:
            st.metric("Prix Actuel", f"{info.get('currentPrice', 0):.2f} €")

        # --- SÉLECTEUR DE PÉRIODE ---
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        choix_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        intervalle = "1m" if choix_p == "1J" else "1d"

        # --- 2. GRAPHIQUE INTERACTIF ET FIGÉ ---
        hist = stock.history(period=p_map[choix_p], interval=intervalle)
        
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['Close'], 
                line=dict(color=couleur, width=2),
                hovertemplate="<b>Date:</b> %{x}<br><b>Prix:</b> %{y:.2f}€<extra></extra>"
            ))

            fig.update_layout(
                template="plotly_dark",
                hovermode="x unified",
                dragmode=False,
                xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
                yaxis=dict(side="right", showgrid=True),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

        # --- 3. ACTUALITÉS ---
        st.divider()
        st.subheader("📰 Actualités Récentes")
        for n in stock.news[:3]:
            st.markdown(f"**{n.get('title')}**")
            st.caption(f"Source: {n.get('publisher')} | [Lire l'original]({n.get('link')})")

    except Exception as e:
        st.error("Action non trouvée. Vérifiez le symbole.")
