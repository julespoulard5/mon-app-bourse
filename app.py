import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="StockVision Pro - FR", layout="wide")

st.title("🚀 StockVision IA")

# --- BARRE DE RECHERCHE ---
with st.form("search_form"):
    col_search, col_button = st.columns([4, 1])
    with col_search:
        ticker_input = st.text_input("Symbole de l'action (ex: AAPL, MC.PA, AIR.LS)", value="AAPL").upper()
    with col_button:
        submitted = st.form_submit_button("Analyser")

st.markdown("---")

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        if info and 'currentPrice' in info:
            # Récupération des données
            nom = info.get('longName', ticker_input)
            prix_brut = info.get('currentPrice')
            devise_origine = info.get('currency', 'USD')
            
            # --- LOGIQUE DE CONVERSION EURO ---
            # Si l'action n'est pas en EUR, on récupère le taux de change
            prix_eur = prix_brut
            symbole_devise = "€"
            
            if devise_origine != "EUR":
                taux = yf.Ticker(f"{devise_origine}EUR=X").info.get('regularMarketPrice', 1)
                prix_eur = prix_brut * taux
            
            # --- AFFICHAGE ---
            col_t, col_p = st.columns([3, 1])
            with col_t:
                st.header(f"📊 {nom}")
            with col_p:
                st.metric("Prix (Estimé en €)", f"{prix_eur:.2f} €")

            # --- CALCULATEUR D'INVESTISSEMENT ---
            with st.expander("💰 Calculateur d'investissement (Euros)"):
                budget = st.number_input("Montant à investir (€)", min_value=0, value=1000)
                quantite = budget / prix_eur
                st.write(f"Avec **{budget} €**, vous achetez environ **{quantite:.2f}** actions.")
                
                cible = info.get('targetMeanPrice', 0)
                if cible:
                    # Conversion de la cible en EUR
                    cible_eur = cible * (taux if devise_origine != "EUR" else 1)
                    profit = (cible_eur - prix_eur) * quantite
                    st.write(f"🎯 Objectif cible : **{cible_eur:.2f} €**")
                    st.write(f"📈 Profit potentiel : **{profit:.2f} €**")

            # --- INDICATEURS EN FRANÇAIS ---
            st.subheader("🤖 Indicateurs Clés")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PER (Valorisation)", f"{info.get('trailingPE', 'N/A')}x")
            m2.metric("ROE (Rentabilité)", f"{info.get('returnOnEquity', 0)*100:.1f}%")
            m3.metric("EBE (EBITDA)", f"{info.get('ebitda', 0)/1e9:.2f} Md")
            m4.metric("Cash-Flow Libre", f"{info.get('freeCashflow', 0)/1e9:.2f} Md")

            # --- GRAPHIQUE PROFESSIONNEL (EN FRANÇAIS) ---
            st.subheader("📈 Évolution du cours (1 an)")
            hist = stock.history(period="1y")
            
            # Création du graphique avec Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Prix de clôture", line=dict(color='#00ff00')))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Prix de l'action",
                template="plotly_dark",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- ACTUALITÉS ---
            st.divider()
            st.subheader("📰 Actualités récentes")
            for n in stock.news[:3]:
                st.write(f"🔹 **[{n['title']}]({n['link']})**")

        else:
            st.warning("⚠️ Action introuvable. Vérifiez le symbole.")

    except Exception as e:
        st.error(f"Erreur de connexion : {e}")

