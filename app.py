import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

# --- BARRE LATÉRALE (NAVIGATION) ---
with st.sidebar:
    st.title("👨‍💻 Jules Trading")
    page = st.radio("Menu", ["🏠 Accueil & Recherche", "📰 Le Flux & Analyse IA"])
    st.markdown("---")
    st.caption("Version 4.0 - Intégration Totale")

# --- BASE DE DONNÉES ACTIONS ---
@st.cache_data
def get_stock_list():
    return {
        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
        "Alphabet (Google)": "GOOGL", "Amazon": "AMZN", "Meta": "META", "Netflix": "NFLX",
        "LVMH": "MC.PA", "L'Oréal": "OR.PA", "Hermès": "RMS.PA", "Airbus": "AIR.PA",
        "TotalEnergies": "TTE.PA", "Sanofi": "SAN.PA", "BNP Paribas": "BNP.PA",
        "ASML": "ASML.AS", "SAP": "SAP.DE", "Siemens": "SIE.DE", "Volkswagen": "VOW3.DE",
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"
    }

# --- ANALYSE IA DES NEWS ---
def get_ia_sentiment(text):
    text = text.lower()
    if any(w in text for w in ['up', 'hausse', 'profit', 'gain', 'buy', 'achat', 'growth', 'record']):
        return "🟢 BULLISH", "L'IA prévoit un impact positif sur le cours."
    if any(w in text for w in ['down', 'baisse', 'chute', 'loss', 'perte', 'sell', 'inflation', 'risk']):
        return "🔴 BEARISH", "L'IA identifie un risque de baisse ou de volatilité."
    return "🟡 NEUTRE", "Information stable, pas d'impact majeur immédiat."

# ==========================================
# PAGE 1 : ACCUEIL & RECHERCHE (Avec Ratios)
# ==========================================
if page == "🏠 Accueil & Recherche":
    st.title("💹 Analyse & Ratios")
    db = get_stock_list()
    choix = st.selectbox("🔍 Rechercher un titre...", options=list(db.keys()), index=None)
    ticker_final = db[choix] if choix else None

    if ticker_final:
        try:
            stock = yf.Ticker(ticker_final)
            # On récupère les infos une seule fois pour éviter le blocage
            info = stock.info
            prix = info.get('currentPrice', 0)
            devise = info.get('currency', 'EUR')

            st.header(f"{info.get('longName', choix)}")
            st.subheader(f"{prix:.2f} {devise}")

            # --- GRAPHIQUE INCROYABLE ---
            p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
            sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
            hist = stock.history(period=p_map[sel_p])
            
            if not hist.empty:
                perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
                fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color=couleur, width=2.5), fill='tozeroy', 
                                         fillcolor=f"rgba(0, 200, 5, 0.1)" if couleur == '#00C805' else "rgba(255, 59, 48, 0.1)"))
                fig.update_layout(template="plotly_dark", hovermode="x unified", dragmode=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # --- RATIOS (PER, ROE) ---
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("PER Actuel", f"{info.get('trailingPE', 0):.2f}x")
            m2.metric("Rentabilité (ROE)", f"{info.get('returnOnEquity', 0)*100:.2f}%")
            m3.metric("PER Moyen (5 ans)", f"{info.get('forwardPE', 0):.2f}x")

            # --- GRAPHIQUE EBE (EBITDA) ---
            st.subheader("📊 Évolution de l'EBE (EBITDA)")
            try:
                ebe = stock.quarterly_financials.loc['EBITDA'].head(10)[::-1]
                st.bar_chart(ebe)
            except:
                st.write("Données financières momentanément indisponibles.")

        except Exception:
            st.error("⚠️ Trop de requêtes. Attendez 30 secondes ou vérifiez la connexion.")

# ==========================================
# PAGE 2 : LE FLUX & ANALYSE IA
# ==========================================
elif page == "📰 Le Flux & Analyse IA":
    st.title("📰 Le Journal Jules Trading")
    tabs = st.tabs(["🇫🇷 France & USA", "🌎 International", "💰 Finance & Crypto"])
    flux_map = {"🇫🇷 France & USA": "^GSPC", "🌎 International": "GC=F", "💰 Finance & Crypto": "BTC-USD"}

    for tab, t_code in zip(tabs, flux_map.values()):
        with tab:
            try:
                news_list = yf.Ticker(t_code).news
                if news_list:
                    for n in news_list[:6]:
                        with st.expander(f"📌 {n.get('title')}", expanded=True):
                            sentiment, explanation = get_ia_sentiment(n.get('title'))
                            c1, c2 = st.columns([1, 2])
                            with c1: st.info(f"**IA : {sentiment}**")
                            with c2: st.write(f"💡 {explanation}")
                            st.caption(f"Source: {n.get('publisher')} | [Lire l'original]({n.get('link')})")
                else: st.write("Aucune news trouvée.")
            except: st.error("Flux indisponible pour le moment.")
