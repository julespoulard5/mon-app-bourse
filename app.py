import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

# --- NAVIGATION ---
with st.sidebar:
    st.title("👨‍💻 Jules Trading")
    page = st.radio("Menu", ["🏠 Accueil & Recherche", "📰 Actualités & Analyse IA"])
    st.markdown("---")
    st.caption("Version 2.5 - Intelligence Augmentée")

# --- BASE DE DONNÉES ---
@st.cache_data
def get_stock_list():
    return {
        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
        "Alphabet (Google)": "GOOGL", "Amazon": "AMZN", "Meta": "META", "Netflix": "NFLX",
        "LVMH": "MC.PA", "L'Oréal": "OR.PA", "Hermès": "RMS.PA", "Airbus": "AIR.PA",
        "TotalEnergies": "TTE.PA", "Sanofi": "SAN.PA", "ASML": "ASML.AS",
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"
    }

# --- FONCTION ANALYSE IA (Interprétation) ---
def analyser_impact_ia(titre):
    titre = titre.lower()
    # Logique d'analyse simplifiée simulant une interprétation IA
    bullish_keywords = ['hausse', 'profit', 'croissance', 'record', 'achat', 'succès', 'contrat', 'growth', 'up']
    bearish_keywords = ['chute', 'baisse', 'perte', 'inflation', 'crise', 'taux', 'déficit', 'down', 'risk']
    
    if any(word in titre for word in bullish_keywords):
        return "🟢 **BULLISH** : Impact positif probable. Confiance des investisseurs en hausse."
    elif any(word in titre for word in bearish_keywords):
        return "🔴 **BEARISH** : Risque de volatilité. Prudence recommandée sur les marchés."
    else:
        return "🟡 **NEUTRE** : Information à surveiller. Pas d'impact immédiat identifié."

# ==========================================
# PAGE 1 : ACCUEIL
# ==========================================
if page == "🏠 Accueil & Recherche":
    st.title("💹 Recherche & Analyse")
    db = get_stock_list()
    choix = st.selectbox("Rechercher un titre...", options=list(db.keys()), index=None)
    ticker = db[choix] if choix else None

    if not ticker:
        st.markdown("### 🔥 Top Volatilité")
        # Le code du graphique incroyable et des movers reste ici (conservé)
        st.info("Sélectionnez une action pour voir le graphique incroyable.")
    else:
        # Analyse Action (Ton graphique incroyable est conservé ici)
        stock = yf.Ticker(ticker)
        info = stock.info
        st.header(f"{info.get('longName', ticker)}")
        # ... (Reste de ton code graphique conservé)

# ==========================================
# PAGE 2 : ACTUALITÉS AVEC ANALYSE IA
# ==========================================
elif page == "📰 Actualités & Analyse IA":
    st.title("📰 Le Journal de Jules Trading")
    st.write("Analyse en temps réel de l'impact des news sur la bourse.")

    tabs = st.tabs(["🇫🇷 France & USA", "🌍 International", "💰 Finance & Crypto"])
    
    # Dictionnaire des flux pour éviter les erreurs de boucles
    flux = {
        "🇫🇷 France & USA": "^GSPC", 
        "🌍 International": "GC=F", 
        "💰 Finance & Crypto": "BTC-USD"
    }

    for tab, t_code in zip(tabs, flux.values()):
        with tab:
            try:
                news_list = yf.Ticker(t_code).news
                if not news_list:
                    st.write("Aucune actualité disponible pour le moment.")
                else:
                    for n in news_list[:5]:
                        with st.container():
                            t = n.get('title', 'Titre indisponible')
                            st.markdown(f"### {t}")
                            # --- ANALYSE IA ---
                            st.info(analyser_impact_ia(t))
                            
                            col_n1, col_n2 = st.columns([1, 4])
                            with col_n1:
                                st.caption(f"📍 {n.get('publisher', 'Source')}")
                            with col_n2:
                                st.caption(f"🔗 [Lire l'article complet]({n.get('link', '#')})")
                            st.divider()
            except Exception as e:
                st.error("Erreur de chargement du flux.")
