import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from googletrans import Translator

# Initialisation du traducteur
translator = Translator()

def traduire(texte):
    try:
        # Traduction vers le français
        return translator.translate(texte, dest='fr').text
    except:
        return texte

# Config de la page
st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision Pro")

# --- 1. BARRE DE RECHERCHE DYNAMIQUE (VRAI AUTO-COMPLETE) ---
# On utilise une liste d'entreprises pour les suggestions
SUGGESTIONS = {
    "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
    "Google": "GOOGL", "Amazon": "AMZN", "LVMH": "MC.PA", "Hermès": "RMS.PA",
    "Airbus": "AIR.PA", "TotalEnergies": "TTE.PA", "Renault": "RNO.PA"
}

recherche = st.text_input("🔍 Recherchez une action (ex: App...)", value="")

ticker_final = None
if recherche:
    # On filtre la liste selon ce que tu tapes
    match = [n for n in SUGGESTIONS.keys() if recherche.lower() in n.lower()]
    if match:
        choix = st.selectbox("Sélectionnez l'entreprise :", match)
        ticker_final = SUGGESTIONS[choix]
    else:
        # Si pas dans la liste, on prend le texte direct (ex: TSLA)
        ticker_final = recherche.upper()

st.markdown("---")

if ticker_final:
    try:
        stock = yf.Ticker(ticker_final)
        info = stock.info
        nom = info.get('longName', ticker_final)
        
        # --- EN-TÊTE ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.header(f"📊 {nom}")
        with c2:
            st.metric("Prix Actuel", f"{info.get('currentPrice', 0):.2f} €")

        # --- SÉLECTEUR DE PÉRIODE ---
        periode_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        choix_p = st.select_slider("Période", options=list(periode_map.keys()), value="1A")
        intervalle = "1m" if choix_p == "1J" else "1d"

        # --- GRAPHIQUE INTERACTIF (FIGÉ AU TOUCHER) ---
        hist = stock.history(period=periode_map[choix_p], interval=intervalle)
        
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['Close'], 
                line=dict(color=couleur, width=2),
                hovertemplate="<b>%{x|%d %b %Y %H:%M}</b><br>Prix: %{y:.2f}€<extra></extra>"
            ))

            fig.update_layout(
                template="plotly_dark",
                hovermode="x unified", # Affiche le prix là où tu touches
                xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
                yaxis=dict(side="right", showgrid=True),
                margin=dict(l=0, r=0, t=10, b=0),
                dragmode=False # Empêche le graphique de bouger quand tu l'effleures
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False, 'scrollZoom': False})

        # --- ACTUALITÉS EN FRANÇAIS ---
        st.divider()
        st.subheader("📰 Dernières Actualités (Traduites)")
        for n in stock.news[:3]:
            titre_fr = traduire(n.get('title'))
            st.markdown(f"**{titre_fr}**")
            st.caption(f"Source: {n.get('publisher')} | [Lire l'article]({n.get('link')})")

    except Exception as e:
        st.error("Action non trouvée. Vérifiez le symbole.")

