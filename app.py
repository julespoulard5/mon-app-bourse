import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

# --- CHARGEMENT DE LA BASE DE DONNÉES ÉLARGIE (Style Trade Republic) ---
@st.cache_data
def get_huge_stock_list():
    # Liste étendue des actions les plus échangées (Europe & US)
    return {
        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
        "Alphabet (Google)": "GOOGL", "Amazon": "AMZN", "Meta (Facebook)": "META",
        "Netflix": "NFLX", "LVMH": "MC.PA", "L'Oréal": "OR.PA", "Hermès": "RMS.PA",
        "Airbus": "AIR.PA", "TotalEnergies": "TTE.PA", "Sanofi": "SAN.PA", 
        "BNP Paribas": "BNP.PA", "Société Générale": "GLE.PA", "Renault": "RNO.PA",
        "Stellantis": "STLAM.PA", "Ferrari": "RACE.MI", "ASML": "ASML.AS",
        "SAP": "SAP.DE", "Siemens": "SIE.DE", "Air Liquide": "AI.PA",
        "Danone": "BN.PA", "Schneider Electric": "SU.PA", "Kering": "KER.PA",
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"
    }

stock_db = get_huge_stock_list()

st.title("💹 Jules Trading")

# --- 1. RECHERCHE DYNAMIQUE (LETTRE PAR LETTRE) ---
# selectbox avec index=None et placeholder simule la barre de recherche TR
choix = st.selectbox(
    "🔍 Rechercher une action ou un symbole...",
    options=list(stock_db.keys()),
    index=None,
    placeholder="Tapez le nom d'une entreprise...",
    key="main_search"
)

# Récupération du ticker : soit depuis la liste, soit saisie libre si possible
ticker_recherche = stock_db[choix] if choix else None

# --- 2. ACCUEIL : TOP VOLATILITÉ (SI PAS DE RECHERCHE) ---
if not ticker_recherche:
    st.markdown("### 🔥 Opportunités du jour")
    
    @st.cache_data(ttl=3600)
    def get_market_movers():
        tickers = ["AAPL", "TSLA", "NVDA", "MC.PA", "TTE.PA", "NFLX", "BTC-USD", "OR.PA"]
        data = yf.download(tickers, period="2d", interval="1d", group_by='ticker', progress=False)
        movers = []
        for t in tickers:
            try:
                h = data[t]
                var = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
                movers.append({'Ticker': t, 'Variation': var, 'Prix': h['Close'].iloc[-1]})
            except: continue
        return pd.DataFrame(movers).sort_values(by='Variation', ascending=False)

    df_movers = get_market_movers()
    c_up, c_down = st.columns(2)
    with c_up:
        for _, r in df_movers.head(4).iterrows():
            st.success(f"**{r['Ticker']}** : +{r['Variation']:.2f}% ({r['Prix']:.2f} €/$)")
    with c_down:
        for _, r in df_movers.tail(4).iloc[::-1].iterrows():
            st.error(f"**{r['Ticker']}** : {r['Variation']:.2f}% ({r['Prix']:.2f} €/$)")

# --- 3. ANALYSE DÉTAILLÉE ---
else:
    try:
        stock = yf.Ticker(ticker_recherche)
        info = stock.info
        prix = info.get('currentPrice', 0)
        devise = info.get('currency', 'EUR')

        st.header(f"{info.get('longName', ticker_recherche)}")
        st.subheader(f"{prix:.2f} {devise}")

        # GRAPHIQUE INTERACTIF (Style Trade Republic)
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        hist = stock.history(period=p_map[sel_p])
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go
