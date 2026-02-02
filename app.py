import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

# --- BARRE LATÉRALE (NAVIGATION) ---
with st.sidebar:
    st.title("👨‍💻 Jules Trading")
    page = st.radio("Menu", ["🏠 Accueil & Recherche", "📰 Actualités du Jour"])
    st.markdown("---")
    st.caption("Version 2.0 - 2026")

# --- FONCTION RECHERCHE DYNAMIQUE ---
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

# ==========================================
# PAGE 1 : ACCUEIL & RECHERCHE
# ==========================================
if page == "🏠 Accueil & Recherche":
    st.title("💹 Recherche d'Actions")
    
    stock_db = get_stock_list()
    choix = st.selectbox(
        "🔍 Rechercher un titre...",
        options=list(stock_db.keys()),
        index=None,
        placeholder="Tapez pour filtrer (ex: Apple, LVMH...)"
    )
    ticker_final = stock_db[choix] if choix else None

    if not ticker_final:
        # --- TOP VOLATILITÉ ---
        st.markdown("### 🔥 Opportunités du jour")
        @st.cache_data(ttl=600)
        def get_market_movers():
            tickers = ["AAPL", "TSLA", "NVDA", "MC.PA", "NFLX", "BTC-USD", "OR.PA", "AMZN"]
            movers = []
            for t in tickers:
                try:
                    h = yf.download(t, period="5d", interval="1d", progress=False)
                    if len(h) >= 2:
                        p_now = float(h['Close'].iloc[-1])
                        p_prev = float(h['Close'].iloc[-2])
                        var = ((p_now - p_prev) / p_prev) * 100
                        movers.append({'Ticker': t, 'Variation': var, 'Prix': p_now})
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
    
    else:
        # --- ANALYSE DÉTAILLÉE ---
        stock = yf.Ticker(ticker_final)
        info = stock.info
        prix = info.get('currentPrice', 0)
        st.header(f"{info.get('longName', ticker_final)}")
        st.subheader(f"{prix:.2f} {info.get('currency', 'EUR')}")

        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        hist = stock.history(period=p_map[sel_p])
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color=couleur, width=2.5), fill='tozeroy', 
                                     fillcolor=f"rgba(0, 200, 5, 0.15)" if couleur == '#00C805' else "rgba(255, 59, 48, 0.15)"))
            fig.update_layout(template="plotly_dark", hovermode="x unified", dragmode=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# PAGE 2 : ACTUALITÉS
# ==========================================
elif page == "📰 Actualités du Jour":
    st.title("📰 Le Journal de Jules Trading")
    st.write("Retrouvez ici l'actualité mondiale et financière filtrée.")

    tab_fr, tab_int, tab_fin = st.tabs(["🇫🇷 France & USA", "🌎 International", "💰 Finance"])

    with tab_fr:
        st.subheader("Actualité France & États-Unis")
        # News via un ticker global (S&P 500) pour avoir les tendances US/FR
        news_global = yf.Ticker("^GSPC").news
        for n in news_global[:5]:
            st.markdown(f"**{n['title']}**")
            st.caption(f"Source: {n['publisher']} | [Lire l'article]({n['link']})")

    with tab_int:
        st.subheader("Monde & Géopolitique")
        # Utilisation de Gold ou Oil pour les news internationales
        news_int = yf.Ticker("GC=F").news
        for n in news_int[:5]:
            st.markdown(f"**{n['title']}**")
            st.caption(f"Source: {n['publisher']} | [Lien]({n['link']})")

    with tab_fin:
        st.subheader("Marchés Financiers")
        news_fin = yf.Ticker("EURUSD=X").news
        for n in news_fin[:5]:
            st.markdown(f"**{n['title']}**")
            st.caption(f"Source: {n['publisher']} | [Lien]({n['link']})")
