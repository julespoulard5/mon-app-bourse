import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Config de la page
st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision Pro")

# --- RECHERCHE ---
recherche = st.text_input("🔍 Recherchez une action (ex: Apple, LVMH, Nvidia...)", value="").strip()

MAPPING = {"APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "GOOGLE": "GOOGL", "LVMH": "MC.PA"}

ticker_final = None
if recherche:
    match = [nom for nom in MAPPING.keys() if recherche.upper() in nom]
    if match:
        choix = st.radio("Suggestions :", match, horizontal=True)
        ticker_final = MAPPING[choix]
    else:
        ticker_final = recherche.upper()

st.markdown("---")

if ticker_final:
    try:
        stock = yf.Ticker(ticker_final)
        info = stock.info
        
        # HEADER
        st.header(f"📊 {info.get('longName', ticker_final)}")
        st.metric("Prix Actuel", f"{info.get('currentPrice', 0):.2f} €")

        # PÉRIODE
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        choix_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        # GRAPHIQUE INTERACTIF FIGÉ
        hist = stock.history(period=p_map[choix_p])
        if not hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Close'],
                line=dict(color='#00C805', width=2),
                hovertemplate="<b>%{x}</b><br>Prix: %{y:.2f}€<extra></extra>"
            ))
            fig.update_layout(
                template="plotly_dark", hovermode="x unified", dragmode=False,
                margin=dict(l=0, r=0, t=10, b=0), height=350
            )
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

        # ACTUALITÉS (Version sans traduction pour éviter le bug)
        st.subheader("📰 Dernières Actualités")
        for n in stock.news[:3]:
            st.markdown(f"**{n.get('title')}**")
            st.caption(f"Source: {n.get('publisher')} | [Lire]({n.get('link')})")

    except Exception as e:
        st.error(f"Erreur : {e}")
