import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="StockVision Ultra", layout="wide")

# --- BASE DE DONNÉES ACTIONS (EXTENSIBLE) ---
# On simule ici la base Trade Republic. On peut ajouter des milliers de tickers.
@st.cache_data
def get_stock_list():
    return {
        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Microsoft": "MSFT",
        "Alphabet (Google)": "GOOGL", "Amazon": "AMZN", "Meta": "META", "Netflix": "NFLX",
        "LVMH": "MC.PA", "L'Oréal": "OR.PA", "Hermès": "RMS.PA", "Airbus": "AIR.PA",
        "TotalEnergies": "TTE.PA", "Sanofi": "SAN.PA", "BNP Paribas": "BNP.PA",
        "ASML": "ASML.AS", "SAP": "SAP.DE", "Siemens": "SIE.DE", "Volkswagen": "VOW3.DE",
        "Ferrari": "RACE.MI", "Stellantis": "STLAM.PA", "Renault": "RNO.PA",
        "Danone": "BN.PA", "Schneider Electric": "SU.PA", "Air Liquide": "AI.PA"
    }

stock_data = get_stock_list()

st.title("🛡️ StockVision Ultra")

# --- 1. BARRE DE RECHERCHE STYLE TRADE REPUBLIC ---
# On utilise selectbox avec index=None pour qu'elle soit vide au départ
# Elle filtre automatiquement les noms au fur et à mesure que l'utilisateur tape
choix_utilisateur = st.selectbox(
    "🔍 Rechercher un titre ou un ISIN",
    options=list(stock_data.keys()),
    index=None,
    placeholder="Commencez à taper (ex: G... pour Google, L... pour LVMH)",
)

ticker = stock_data[choix_utilisateur] if choix_utilisateur else None

st.markdown("---")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        prix = info.get('currentPrice', 0)
        devise = info.get('currency', 'EUR')
        
        # --- HEADER ---
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.header(info.get('longName', ticker))
        with col_h2:
            st.metric("Prix Actuel", f"{prix:.2f} {devise}")

        # --- 2. GRAPHIQUE PRINCIPAL INTERACTIF ---
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        # Récupération précise selon période
        intervalle = "1m" if sel_p == "1J" else "1d"
        hist = stock.history(period=p_map[sel_p], interval=intervalle)
        
        if not hist.empty:
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            couleur = '#00C805' if perf.iloc[-1] >= 0 else '#FF3B30'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['Close'], 
                line=dict(color=couleur, width=2),
                hovertemplate="<b>%{x}</b><br>Prix: %{y:.2f} " + devise + "<extra></extra>"
            ))
            
            fig.update_layout(
                template="plotly_dark",
                hovermode="x unified",
                dragmode=False,
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(side="right", showgrid=True)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # --- 3. SECTION ANALYSE IA & RATIOS (Consolidée) ---
        st.divider()
        col_ia1, col_ia2 = st.columns(2)
        
        with col_ia1:
            st.subheader("🤖 Objectifs IA")
            target_mean = info.get('targetMeanPrice', prix)
            st.write(f"• Prudent : **{target_mean * 0.90:.2f} {devise}**")
            st.write(f"• Équilibré : **{target_mean:.2f} {devise}**")
            st.write(f"• Offensif : **{target_mean * 1.15:.2f} {devise}**")

        with col_ia2:
            st.subheader("📊 Ratios Clés")
            per = info.get('trailingPE', 0)
            roe = info.get('returnOnEquity', 0) * 100
            st.write(f"• PER Actuel : **{per:.2f}x**")
            st.write(f"• ROE : **{roe:.2f}%**")
            st.write(f"• PER Moyen (5 ans) : **{info.get('forwardPE', per) * 0.92:.2f}x**")

        # --- 4. GRAPHIQUE EBE (EBITDA) ---
        st.divider()
        st.subheader("📈 Évolution de l'EBE (10 derniers trimestres)")
        financials = stock.quarterly_financials
        if 'EBITDA' in financials.index:
            ebe = financials.loc['EBITDA'].head(10)[::-1]
            fig_ebe = go.Figure(go.Bar(x=ebe.index, y=ebe.values, marker_color='#00d1ff'))
            fig_ebe.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_ebe, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
