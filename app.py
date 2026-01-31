import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="StockVision Pro", layout="wide")

# --- LISTE DE RÉFÉRENCE POUR LES SUGGESTIONS ---
# Liste étendue des actions populaires (Tu peux en ajouter d'autres ici)
SUGGESTIONS = [
    "AAPL (Apple)", "MSFT (Microsoft)", "TSLA (Tesla)", "NVDA (NVIDIA)", 
    "AMZN (Amazon)", "GOOGL (Google)", "META (Meta)", "NFLX (Netflix)",
    "MC.PA (LVMH)", "OR.PA (L'Oréal)", "RMS.PA (Hermès)", "AIR.PA (Airbus)",
    "TTE.PA (TotalEnergies)", "SAN.PA (Sanofi)", "BNP.PA (BNP Paribas)",
    "ASML.AS (ASML)", "SAP.DE (SAP)", "SIE.DE (Siemens)", "VOW3.DE (Volkswagen)"
]

st.title("🚀 StockVision : Analyse & Comparaison Intuitive")

# --- 1. RECHERCHE PRINCIPALE AVEC AUTO-COMPLÉTION ---
choix_principal = st.selectbox(
    "🔍 Recherchez l'entreprise principale :",
    options=[""] + SUGGESTIONS,
    format_func=lambda x: x if x != "" else "Tapez le nom d'une entreprise...",
    key="main_search"
)

# Extraction du symbole (Ticker)
ticker_principal = choix_principal.split(" (")[0] if " (" in choix_principal else choix_principal

st.markdown("---")

if ticker_principal:
    try:
        stock = yf.Ticker(ticker_principal)
        info = stock.info
        
        if 'currentPrice' in info:
            nom = info.get('longName', ticker_principal)
            prix = info.get('currentPrice')
            devise = info.get('currency', 'EUR')
            per_actuel = info.get('trailingPE')
            per_moyen_hist = info.get('forwardPE', 20.0) # On utilise le Forward PE comme base de comparaison

            # --- HEADER ---
            col_t, col_p = st.columns([3, 1])
            with col_t:
                st.header(f"📊 {nom}")
            with col_p:
                st.metric("Prix Actuel", f"{prix:.2f} {devise}")

            # --- ANALYSE PER ---
            st.subheader("⚖️ Valorisation (PER actuel vs historique)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("PER Actuel", f"{per_actuel:.2f}x" if per_actuel else "N/A")
            with c2:
                st.metric("PER de Référence", f"{per_moyen_hist:.2f}x")
            with c3:
                if per_actuel and per_moyen_hist:
                    diff = ((per_actuel - per_moyen_hist) / per_moyen_hist) * 100
                    if diff < 0:
                        st.success(f"DÉCOTE : -{abs(diff):.1f}%")
                    else:
                        st.warning(f"SURCOTE : +{diff:.1f}%")

            # --- 2. GRAPHIQUE AVEC "+" (SUGGESTIONS POUR COMPARAISON) ---
            st.subheader("📈 Comparaison des performances (%)")
            
            # Ici on utilise aussi la liste de suggestions pour le comparateur
            comparaison_list = st.multiselect(
                "➕ Ajouter des entreprises pour comparer :",
                options=SUGGESTIONS,
                help="Sélectionnez d'autres entreprises pour superposer leurs graphiques."
            )

            # Données du graphique (période 1 an par défaut)
            hist_p = stock.history(period="1y")['Close']
            fig = go.Figure()

            # Courbe principale (Normalisée à 0% au début)
            perf_p = (hist_p / hist_p.iloc[0] - 1) * 100
            fig.add_trace(go.Scatter(x=hist_p.index, y=perf_p, name=nom, line=dict(width=3)))

            # Ajout des courbes comparatives
            if comparaison_list:
                for comp in comparaison_list:
                    t_comp = comp.split(" (")[0]
                    hist_c = yf.Ticker(t_comp).history(period="1y")['Close']
                    if not hist_c.empty:
                        perf_c = (hist_c / hist_c.iloc[0] - 1) * 100
                        fig.add_trace(go.Scatter(x=hist_c.index, y=perf_c, name=comp))

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Variation du cours (%)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- STRATÉGIE & NEWS ---
            st.divider()
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("🎯 Axes de Développement")
                st.write(info.get('longBusinessSummary', "N/A")[:700] + "...")
            with col_right:
                st.subheader("📰 Actualités")
                for n in stock.news[:3]:
                    st.write(f"🔹 **[{n.get('title')}]({n.get('link')})**")

        else:
            st.error("Données non disponibles pour ce symbole.")
    except Exception as e:
        st.error(f"Erreur : {e}")

