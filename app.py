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
    st.caption("Version 3.0 - Lecture Directe")

# --- BASE DE DONNÉES ACTIONS ---
@st.cache_data
def get_stock_list():
    return {
        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
        "Alphabet (Google)": "GOOGL", "Amazon": "AMZN", "Meta": "META", "LVMH": "MC.PA", 
        "Airbus": "AIR.PA", "TotalEnergies": "TTE.PA", "Bitcoin": "BTC-USD"
    }

# --- ANALYSE IA SIMPLIFIÉE ---
def get_ia_sentiment(text):
    text = text.lower()
    if any(w in text for w in ['up', 'hausse', 'profit', 'gain', 'buy', 'achat', 'growth']):
        return "🟢 POSITIF (BULLISH)", "L'IA prévoit une tendance haussière suite à cette annonce."
    if any(w in text for w in ['down', 'baisse', 'chute', 'loss', 'perte', 'sell', 'inflation']):
        return "🔴 NÉGATIF (BEARISH)", "L'IA identifie un risque de baisse immédiat."
    return "🟡 NEUTRE", "Information stable, pas d'impact majeur sur le cours détecté."

# ==========================================
# PAGE 1 : ACCUEIL & RECHERCHE
# ==========================================
if page == "🏠 Accueil & Recherche":
    st.title("💹 Analyse Boursière")
    db = get_stock_list()
    choix = st.selectbox("Rechercher un titre...", options=list(db.keys()), index=None)
    ticker = db[choix] if choix else None

    if ticker:
        try:
            stock = yf.Ticker(ticker)
            # Utilisation de fast_info pour éviter le RateLimit de .info
            price = stock.fast_info['last_price']
            currency = stock.fast_info['currency']
            
            st.header(f"{choix} ({ticker})")
            st.subheader(f"{price:.2f} {currency}")

            # Graphique "Incroyable" conservé
            p_map = {"1J": "1d", "1M": "1mo", "1A": "1y", "MAX": "max"}
            sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
            hist = stock.history(period=p_map[sel_p])
            
            if not hist.empty:
                fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#00C805', width=2), fill='tozeroy', fillcolor='rgba(0,200,5,0.1)'))
                fig.update_layout(template="plotly_dark", hovermode="x unified", height=400, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.error("⚠️ Limite de requêtes atteinte. Réessayez dans 1 minute.")

# ==========================================
# PAGE 2 : ACTUALITÉS (LECTURE DIRECTE)
# ==========================================
elif page == "📰 Actualités & Analyse IA":
    st.title("📰 Le Flux Jules Trading")
    
    # On utilise des tickers stables pour le flux
    categories = {"🇫🇷 France & USA": "^GSPC", "🌎 International": "GC=F", "💰 Finance & Crypto": "BTC-USD"}
    
    selected_tab = st.tabs(list(categories.keys()))

    for i, (name, t_code) in enumerate(categories.items()):
        with selected_tab[i]:
            try:
                news = yf.Ticker(t_code).news
                if not news:
                    st.warning("Aucune info disponible pour le moment.")
                else:
                    for n in news[:8]: # Plus d'articles
                        # Design "Card" pour lecture directe
                        with st.expander(f"📌 {n.get('title')}", expanded=True):
                            sentiment, explanation = get_ia_sentiment(n.get('title'))
                            
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.markdown(f"**Analyse IA :**\n\n{sentiment}")
                            with c2:
                                st.write(f"💡 {explanation}")
                            
                            st.caption(f"Source: {n.get('publisher')} | [Lien source]({n.get('link')})")
            except Exception:
                st.error("Flux temporairement indisponible.")
