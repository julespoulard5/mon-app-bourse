import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

st.title("💹 Jules Trading")

# --- 1. BASE DE DONNÉES DE RECHERCHE (STREMLIT SELECTBOX) ---
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

stock_db = get_stock_list()

# Barre de recherche avec autocomplétion
choix = st.selectbox(
    "🔍 Rechercher une action (Tapez les premières lettres)...",
    options=list(stock_db.keys()),
    index=None,
    placeholder="Ex: Apple, LVMH, Tesla..."
)

ticker_final = stock_db[choix] if choix else None

# --- 2. ACCUEIL : TOP VOLATILITÉ (SI PAS DE RECHERCHE) ---
if not ticker_final:
    st.markdown("### 🔥 Opportunités du jour")
    
    @st.cache_data(ttl=3600)
    def get_market_movers():
        tickers = ["AAPL", "TSLA", "NVDA", "MC.PA", "NFLX", "BTC-USD", "OR.PA", "AMZN"]
        data = yf.download(tickers, period="2d", interval="1d", group_by='ticker', progress=False)
        movers = []
        for t in tickers:
            try:
                h = data[t]
                var = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
                movers.append({'Ticker': t, 'Variation': var, 'Prix': h['Close'].iloc[-1]})
            except: continue
        return pd.DataFrame(movers).sort_values(by='Variation', ascending=False)

    try:
        df_movers = get_market_movers()
        c_up, c_down = st.columns(2)
        with c_up:
            st.write("📈 **Plus fortes hausses**")
            for _, r in df_movers.head(4).iterrows():
                st.success(f"**{r['Ticker']}** : +{r['Variation']:.2f}% ({r['Prix']:.2f} €/$)")
        with c_down:
            st.write("📉 **Plus fortes baisses**")
            for _, r in df_movers.tail(4).iloc[::-1].iterrows():
                st.error(f"**{r['Ticker']}** : {r['Variation']:.2f}% ({r['Prix']:.2f} €/$)")
    except:
        st.info("Chargement des données de marché...")

# --- 3. ANALYSE DÉTAILLÉE ---
else:
    try:
        stock = yf.Ticker(ticker_final)
        info = stock.info
        prix = info.get('currentPrice', 0)
        devise = info.get('currency', 'EUR')

        # Header
        st.header(f"{info.get('longName', ticker_final)}")
        st.subheader(f"{prix:.2f} {devise}")

        # Graphique interactif (Style Trade Republic)
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        hist = stock.history(period=p_map[sel_p])
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Close'], 
                line=dict(color=couleur, width=2), 
                fill='tozeroy',
                hovertemplate="<b>Date:</b> %{x}<br><b>Prix:</b> %{y:.2f} " + devise + "<extra></extra>"
            ))
            fig.update_layout(
                template="plotly_dark", 
                hovermode="x unified", 
                dragmode=False, 
                height=400, 
                margin=dict(l=0,r=0,t=0,b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(side="right")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Objectifs IA et Stats
        st.divider()
        col1, col2, col3 = st.columns(3)
        target = info.get('targetMeanPrice', prix)
        
        col1.metric("Objectif Prudent", f"{target*0.95:.2f} {devise}")
        col2.metric("Objectif Équilibré", f"{target:.2f} {devise}")
        col3.metric("Objectif Offensif", f"{target*1.10:.2f} {devise}")

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("PER Actuel", f"{info.get('trailingPE', 0):.2f}x")
        m2.metric("Rentabilité (ROE)", f"{info.get('returnOnEquity', 0)*100:.2f}%")
        m3.metric("PER Moyen (5 ans)", f"{info.get('forwardPE', 0):.2f}x")

        # Graphique EBE (EBITDA)
        st.subheader("📊 Évolution de l'EBE (EBITDA)")
        try:
            ebe = stock.quarterly_financials.loc['EBITDA'].head(10)[::-1]
            st.bar_chart(ebe)
        except:
            st.write("Données d'EBE indisponibles pour ce titre.")

    except Exception as e:
        st.error(f"Erreur lors de la récupération : {e}")
