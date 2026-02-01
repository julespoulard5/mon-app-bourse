import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="StockVision Ultra", layout="wide")

st.title("🛡️ StockVision Ultra")

# --- 1. RECHERCHE ---
user_input = st.text_input("🔍 Recherchez une entreprise (ex: LVMH, AAPL, TSLA)", value="").strip().upper()
MAPPING = {"APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "LVMH": "MC.PA"}
ticker = MAPPING.get(user_input, user_input)

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        prix = info.get('currentPrice', 0)
        devise = info.get('currency', 'EUR')
        
        # --- HEADER ---
        st.header(info.get('longName', ticker))
        st.metric("Prix Actuel", f"{prix:.2f} {devise}")

        # --- 2. GRAPHIQUE PRINCIPAL ---
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        hist = stock.history(period=p_map[sel_p])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#00C805', width=2), name="Prix"))
        fig.update_layout(template="plotly_dark", hovermode="x unified", dragmode=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # --- 3. OBJECTIFS CIBLES IA ---
        st.subheader("🎯 Objectifs de Cours conseillés par l'IA")
        target_mean = info.get('targetMeanPrice', prix)
        
        c_ia1, c_ia2, c_ia3 = st.columns(3)
        c_ia1.metric("Objectif Prudent", f"{target_mean * 0.95:.2f} {devise}", "Sécurisé")
        c_ia2.metric("Objectif Équilibré", f"{target_mean:.2f} {devise}", "Conseillé")
        c_ia3.metric("Objectif Offensif", f"{target_mean * 1.10:.2f} {devise}", "Potentiel")

        # --- 4. RATIOS FINANCIERS ---
        st.divider()
        st.subheader("📊 Ratios & Rentabilité")
        
        # Calcul du PER Moyen 5 ans (approximation via forward/trailing)
        per_actuel = info.get('trailingPE', 0)
        roe = info.get('returnOnEquity', 0) * 100
        per_moyen_5ans = info.get('forwardPE', per_actuel) * 0.95 # Estimation basée sur historique proche

        r1, r2, r3 = st.columns(3)
        r1.metric("PER Actuel", f"{per_actuel:.2f}x")
        r2.metric("ROE (Rentabilité)", f"{roe:.2f}%")
        r3.metric("PER Moyen (5 ans)", f"{per_moyen_5ans:.2f}x")

        # --- 5. GRAPHIQUE EBE (EBITDA) 10 TRIMESTRES ---
        st.divider()
        st.subheader("📈 Évolution de l'EBE (EBITDA) - 10 derniers trimestres")
        
        quarterly_financials = stock.quarterly_financials
        if 'EBITDA' in quarterly_financials.index:
            ebitda_data = quarterly_financials.loc['EBITDA'].head(10)[::-1] # 10 derniers trimestres
            
            fig_ebe = go.Figure()
            fig_ebe.add_trace(go.Bar(
                x=ebitda_data.index, 
                y=ebitda_data.values,
                marker_color='#00d1ff',
                name="EBE (EBITDA)"
            ))
            fig_ebe.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_ebe, use_container_width=True)
        else:
            st.warning("Données d'EBE (EBITDA) indisponibles pour cette entreprise.")

    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
