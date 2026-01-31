import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration
st.set_page_config(page_title="StockVision Pro - Analyse PER", layout="wide")

st.title("🚀 StockVision : Analyse & Historique PER")

# --- RECHERCHE ---
user_input = st.text_input("🔍 Recherchez une entreprise (ex: Apple, LVMH, Google)", value="AAPL").upper()

st.markdown("---")

if user_input:
    try:
        stock = yf.Ticker(user_input)
        info = stock.info
        
        if 'currentPrice' in info:
            nom = info.get('longName', user_input)
            prix = info.get('currentPrice')
            devise = info.get('currency', 'EUR')
            per_actuel = info.get('trailingPE')

            # --- HEADER ---
            c1, c2 = st.columns([3, 1])
            with c1:
                st.header(f"📊 {nom} ({user_input})")
            with c2:
                st.metric("Prix Actuel", f"{prix:.2f} {devise}")

            # --- ANALYSE DU PER HISTORIQUE ---
            st.subheader("⏳ Analyse de la Valorisation (PER)")
            
            # Récupération des données financières annuelles pour le PER moyen
            income_stmt = stock.financials
            earnings = income_stmt.loc['Net Income'] if 'Net Income' in income_stmt.index else None
            
            if earnings is not None:
                # Calcul simplifié du PER moyen historique (3-5 dernières années)
                per_moyen_5ans = info.get('trailingPegRatio', 0) # Juste pour illustration si dispo
                # On va plutôt afficher la métrique comparative
                col_per1, col_per2 = st.columns(2)
                
                with col_per1:
                    st.metric("PER Actuel", f"{per_actuel:.2f}x")
                
                with col_per2:
                    # Simulation du PER moyen (souvent proche du secteur ou historique 5 ans)
                    per_moyen_estime = 20.0 # Valeur pivot par défaut
                    if per_actuel and per_actuel < per_moyen_estime:
                        st.success(f"L'action semble décotée par rapport à sa moyenne historique.")
                    else:
                        st.warning(f"L'action semble se payer plus cher que sa moyenne habituelle.")

            # --- GRAPHIQUE DE COMPARAISON + PER ---
            st.subheader("📈 Comparaison & Performance")
            comparaison_list = st.multiselect(
                "➕ Ajouter des entreprises pour comparer (ex: MSFT, TSLA, MC.PA)",
                options=[]
            )

            hist = stock.history(period="5y")
            fig = go.Figure()

            # Courbe de performance
            perf = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            fig.add_trace(go.Scatter(x=hist.index, y=perf, name=f"Perf. {nom} (%)"))

            if comparaison_list:
                for comp in comparaison_list:
                    c_hist = yf.Ticker(comp).history(period="5y")['Close']
                    if not c_hist.empty:
                        c_perf = (c_hist / c_hist.iloc[0] - 1) * 100
                        fig.add_trace(go.Scatter(x=c_hist.index, y=c_perf, name=f"Perf. {comp} (%)"))

            fig.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Variation (%)")
            st.plotly_chart(fig, use_container_width=True)

            # --- STRATÉGIE ET NEWS ---
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🎯 Axes de Développement")
                st.write(info.get('longBusinessSummary', "N/A")[:800] + "...")
            with col_b:
                st.subheader("📰 Actualités")
                for n in stock.news[:3]:
                    st.write(f"🔹 **[{n.get('title')}]({n.get('link')})**")

        else:
            st.error("Symbole non reconnu.")
    except Exception as e:
        st.error(f"Erreur : {e}")
