import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from googletrans import Translator

# Initialisation du traducteur
translator = Translator()

def traduire(texte):
    try:
        # On traduit le titre en français
        return translator.translate(texte, dest='fr').text
    except:
        return texte # Si erreur, on garde l'original

st.set_page_config(page_title="StockVision Pro", layout="wide")

st.title("🚀 StockVision Pro")

# --- 1. BARRE DE RECHERCHE ÉPURÉE (SANS LISTE DÉROULANTE) ---
# L'utilisateur tape son texte librement
recherche = st.text_input("🔍 Recherchez une entreprise (ex: Apple, LVMH, Nvidia...)", value="").strip()

# Petit dictionnaire d'aide pour les noms courants
AIDE_RECHERCHE = {
    "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "GOOGLE": "GOOGL",
    "LVMH": "MC.PA", "AIRBUS": "AIR.PA", "HERMES": "RMS.PA", "TOTAL": "TTE.PA"
}

ticker_final = None
if recherche:
    # On propose des suggestions SEULEMENT si l'utilisateur tape quelque chose
    match = [nom for nom in AIDE_RECHERCHE.keys() if recherche.upper() in nom]
    
    if match:
        choix = st.radio("C'est l'une de ces entreprises ?", match, horizontal=True)
        ticker_final = AIDE_RECHERCHE[choix]
    else:
        # Sinon on prend le code tapé directement (ex: AAPL)
        ticker_final = recherche.upper()

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
                hovertemplate="<b>%{x}</b><br>Prix: %{y:.2f}€<extra></extra>"
            ))

            fig.update_layout(
                template="plotly_dark",
                hovermode="x unified", # Affiche le prix et la date là où on touche
                dragmode=False,        # Empêche de déplacer le graphique (reste figé)
                xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
                yaxis=dict(side="right", showgrid=True),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350
            )
            
            # Affichage avec interactivité mobile
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

        # --- 3. ACTUALITÉS EN FRANÇAIS ---
        st.divider()
        st.subheader("📰 Actualités Récentes (Traduites)")
        with st.spinner('Traduction des news...'):
            for n in stock.news[:3]:
                titre_fr = traduire(n.get('title'))
                st.markdown(f"**{titre_fr}**")
                st.caption(f"Source: {n.get('publisher')} | [Lire]({n.get('link')})")

    except Exception as e:
        st.error(f"Erreur de recherche. Vérifiez le symbole ou le nom.")


