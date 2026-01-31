import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from googletrans import Translator

# Initialisation du traducteur
translator = Translator()

def traduire(texte):
    try:
        # Traduction rapide en français
        return translator.translate(texte, dest='fr').text
    except:
        return texte

# Configuration de l'app
st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision Pro")

# --- 1. BARRE DE RECHERCHE ÉPURÉE ---
# On utilise un text_input pour éviter le volet déroulant automatique
recherche = st.text_input("🔍 Recherchez une action (ex: Apple, LVMH, TSLA)", value="").strip()

# Base de données pour faire correspondre les noms aux symboles
BASE_ACTIONS = {
    "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "MICROSOFT": "MSFT",
    "GOOGLE": "GOOGL", "AMAZON": "AMZN", "LVMH": "MC.PA", "HERMES": "RMS.PA",
    "AIRBUS": "AIR.PA", "TOTAL": "TTE.PA", "RENAULT": "RNO.PA", "DANONE": "BN.PA"
}

# Logique de suggestion dynamique
ticker_final = None
if recherche:
    # On cherche si ce que l'utilisateur tape correspond au début d'un nom ou d'un ticker
    suggestions = [k for k in BASE_ACTIONS.keys() if k.startswith(recherche.upper())]
    if suggestions:
        choix = st.selectbox("Suggestions trouvées :", suggestions)
        ticker_final = BASE_ACTIONS[choix]
    else:
        # Si pas dans la liste, on tente de prendre le texte brut (ex: AAPL)
        ticker_final = recherche.upper()

st.markdown("---")

if ticker_final:
    try:
        stock = yf.Ticker(ticker_final)
        info = stock.info
        nom = info.get('longName', ticker_final)
        
        # --- HEADER ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.header(f"📊 {nom}")
        with c2:
            st.metric("Prix Actuel", f"{info.get('currentPrice', 0):.2f} €")

        # --- SÉLECTEUR PÉRIODE ---
        periode_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        choix_p = st.select_slider("Période", options=list(periode_map.keys()), value="1A")
        intervalle = "1m" if choix_p == "1J" else "1d"

        # --- GRAPHIQUE INTERACTIF ---
        hist = stock.history(period=periode_map[choix_p], interval=intervalle)
        
        if not hist.empty:
            # Calcul de la performance
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['Close'], 
                name="Prix",
                line=dict(color=couleur, width=2),
                hovertemplate="<b>Date:</b> %{x}<br><b>Prix:</b> %{y:.2f}€<extra></extra>"
            ))

            fig.update_layout(
                template="plotly_dark",
                hovermode="x unified", # La ligne reste figée sur l'axe X quand on touche
                xaxis=dict(showgrid=False, title="Date"),
                yaxis=dict(showgrid=True, title="Prix (€)", side="right"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=400,
                spikedistance=-1, # Force la ligne de repère
            )
            
            # Paramètres pour le mobile : le graphique réagit au clic/toucher
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # --- ACTUALITÉS EN FRANÇAIS ---
        st.divider()
        st.subheader("📰 Actualités Récentes")
        with st.spinner('Traduction en cours...'):
            for n in stock.news[:3]:
                titre_fr = traduire(n.get('title'))
                st.markdown(f"**{titre_fr}**")
                st.caption(f"Source: {n.get('publisher')} | [Lien]({n.get('link')})")

    except Exception as e:
        st.error(f"Action non trouvée ou erreur réseau.")
