import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration Jules Trading
st.set_page_config(page_title="Jules Trading", layout="wide")

st.title("💹 Jules Trading")

# --- 1. RECHERCHE UNIVERSELLE ---
# On propose quelques suggestions, mais l'utilisateur peut taper n'importe quel Ticker
SUGGESTIONS = ["AAPL", "TSLA", "NVDA", "MC.PA", "TTE.PA", "BTC-USD", "MSFT", "AMZN"]
search_query = st.text_input("🔍 Recherchez une action, un indice ou une crypto (ex: Apple, LVMH, AAPL, BTC-USD)", value="").strip().upper()

# --- 2. LOGIQUE D'AFFICHAGE ACCUEIL (SI PAS DE RECHERCHE) ---
if not search_query:
    st.subheader("🔥 Opportunités du jour (Plus fortes variations)")
    
    @st.cache_data(ttl=3600)
    def get_market_movers():
        # On scanne un échantillon représentatif pour trouver la volatilité
        tickers = ["AAPL", "TSLA", "NVDA", "AMD", "META", "NFLX", "PYPL", "BABA", "MC.PA", "OR.PA", "AIR.PA"]
        data = yf.download(tickers, period="2d", interval="1d", group_by='ticker', progress=False)
        movers = []
        for t in tickers:
            try:
                hist = data[t]
                change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                movers.append({'Ticker': t, 'Variation': change, 'Prix': hist['Close'].iloc[-1]})
            except: continue
        return pd.DataFrame(movers).sort_values(by='Variation', ascending=False)

    try:
        df_movers = get_market_movers()
        top_hausses = df_movers.head(4)
        top_baisses = df_movers.tail(4).iloc[::-1]

        col_up, col_down = st.columns(2)
        with col_up:
            st.write("📈 **Top Hausses**")
            for _, row in top_hausses.iterrows():
                st.success(f"**{row['Ticker']}** : {row['Variation']:.2f}% ({row['Prix']:.2f} €/$)")
        with col_down:
            st.write("📉 **Top Baisses**")
            for _, row in top_baisses.iterrows():
                st.error(f"**{row['Ticker']}** : {row['Variation']:.2f}% ({row['Prix']:.2f} €/$)")
    except:
        st.info("Chargement des données de marché...")

# --- 3. ANALYSE DE L'ACTION SÉLECTIONNÉE ---
else:
    try:
        # On tente de trouver l'action
        stock = yf.Ticker(search_query)
        info = stock.info
        
        # Si Yahoo ne trouve pas par le nom, on prévient
        if 'currentPrice' not in info:
            st.warning(f"Aucun résultat précis pour '{search_query}'. Essayez avec le symbole exact (ex: AAPL pour Apple).")
        else:
            prix = info.get('currentPrice', 0)
            devise = info.get('currency', 'EUR')
            
            # HEADER
            st.header(f"{info.get('longName', search_query)}")
            st.subheader(f"{prix:.2f} {devise}")

            # GRAPHIQUE INTERACTIF
            p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
            sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
            hist = stock.history(period=p_map[sel_p])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#00C805', width=2), fill='tozeroy', name="Prix"))
            fig.update_layout(template="plotly_dark", hovermode="x unified", dragmode=False, height=400, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

            # RATIOS ET IA (Mémorisés)
            st.divider()
            c1, c2, c3 = st.columns(3)
            per = info.get('trailingPE', 0)
            roe = info.get('returnOnEquity', 0) * 100
            target = info.get('targetMeanPrice', prix)
            
            c1.metric("PER Actuel", f"{per:.2f}x")
            c2.metric("Rentabilité (ROE)", f"{roe:.2f}%")
            c3.metric("Cible IA", f"{target:.2f} {devise}")

            # EBE / EBITDA
            st.subheader("📊 Performance Opérationnelle (EBE)")
            try:
                ebe = stock.quarterly_financials.loc['EBITDA'].head(10)[::-1]
                st.bar_chart(ebe)
            except:
                st.write("Données trimestrielles indisponibles.")

    except Exception as e:
        st.error(f"Erreur : {e}")
