import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from googletrans import Translator

# Initialisation du traducteur
translator = Translator()

def traduire(texte):
    try:
        return translator.translate(texte, dest='fr').text
    except:
        return texte

# Configuration de l'app
st.set_page_config(page_title="StockVision Pro", layout="wide")

# --- UNIVERS D'ACTIONS ---
@st.cache_data
def get_stock_universe():
    return [
        "AAPL (Apple)", "GOOGL (Google)", "MSFT (Microsoft)", "TSLA (Tesla)", 
        "NVDA (NVIDIA)", "AMZN (Amazon)", "META (Meta)", "NFLX (Netflix)",
        "MC.PA (LVMH)", "OR.PA (L'Oréal)", "RMS.PA (Hermès)", "AIR.PA (Airbus)",
        "TTE.PA (TotalEnergies)", "SAN.PA (Sanofi)", "BNP.PA (BNP Paribas)",
        "ASML.AS (ASML)", "SAP.DE (SAP)", "SIE.DE (Siemens)", "VOW3.DE (Volkswagen)"
    ]

universe = get_stock_universe()

st.title("🚀 StockVision Pro")

# --- 1. RECHERCHE DYNAMIQUE ---
main_choice = st.selectbox(
    "🔍 Rechercher une entreprise :",
    options=universe,
    index=None,
    placeholder="Tapez le nom ou le symbole...",
    key="main_search"
)

main_ticker = main_choice.split(" (")[0] if main_choice else None

if main_ticker:
    try:
        stock = yf.Ticker(main_ticker)
        info = stock.info
        nom = info.get('longName', main_ticker)
        
        # --- HEADER PRIX ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.header(f"📊 {nom}")
        with c2:
            st.metric("Prix Actuel", f"{info.get('currentPrice', 0):.2f} €")

        # --- 2. SÉLECTEUR DE PÉRIODE (STYLE TRADE REPUBLIC) ---
        st.write("---")
        periode_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        choix_p = st.select_slider("Période", options=list(periode_map.keys()), value="1A")
        
        intervalle = "1m" if choix_p == "1J" else "1d"
        st.subheader(f"📈 Performance ({choix_p})")

        # --- 3. SUPERPOSITION ---
        compare_selections = st.multiselect(
            "➕ Comparer avec une autre action :",
            options=universe,
            placeholder="Tapez pour ajouter..."
        )

        # Données
        hist_main = stock.history(period=periode_map[choix_p], interval=intervalle)['Close']
        
        if not hist_main.empty:
            fig = go.Figure()
            perf_main = (hist_main / hist_main.iloc[0] - 1) * 100
            
            # Couleur dynamique (Vert/Rouge)
            couleur = '#00C805' if perf_main.iloc[-1] >= 0 else '#FF3B30'
            
            fig.add_trace(go.Scatter(
                x=hist_main.index, y=perf_main, name=nom,
                line=dict(color=couleur, width=3),
                fill='tozeroy',
                fillcolor=f"rgba(0, 200, 5, 0.1)" if couleur == '#00C805' else "rgba(255, 59, 48, 0.1)"
            ))

            if compare_selections:
                for selection in compare_selections:
                    t_comp = selection.split(" (")[0]
                    h_comp = yf.Ticker(t_comp).history(period=periode_map[choix_p], interval=intervalle)['Close']
                    if not h_comp.empty:
                        p_comp = (h_comp / h_comp.iloc[0] - 1) * 100
                        fig.add_trace(go.Scatter(x=h_comp.index, y=p_comp, name=selection))

            fig.update_layout(
                template="plotly_dark",
                yaxis=dict(title="Variation (%)", side="right"),
                hovermode="x unified",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- 4. ACTUALITÉS TRADUITES ---
        st.divider()
        st.subheader("📰 Actualités en Direct (Traduites)")
        with st.spinner('Traduction des dernières nouvelles...'):
            for n in stock.news[:4]:
                titre_fr = traduire(n.get('title'))
                st.write(f"🔹 **{titre_fr}**")
                st.caption(f"Source: {n.get('publisher')} | [Lire l'original]({n.get('link')})")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
