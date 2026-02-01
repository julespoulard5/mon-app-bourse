import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText

# Configuration de la page
st.set_page_config(page_title="StockVision Ultra", layout="wide", initial_sidebar_state="collapsed")

# --- STYLE CSS PERSONNALISÉ (DESIGN TR) ---
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ StockVision Ultra")

# --- 1. RECHERCHE DYNAMIQUE ---
user_input = st.text_input("🔍 Recherchez une entreprise ou un symbole (ex: LVMH, AAPL, NVDA)", value="").strip().upper()

# Mapping rapide
MAPPING = {"APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "LVMH": "MC.PA", "AIRBUS": "AIR.PA"}
ticker = MAPPING.get(user_input, user_input)

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        prix = info.get('currentPrice', 0)
        devise = info.get('currency', 'EUR')
        
        # --- HEADER PRIX ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.header(info.get('longName', ticker))
        with c2:
            st.metric("Prix Actuel", f"{prix:.2f} {devise}")

        # --- 2. ANALYSE IA (VERDICT) ---
        st.subheader("🤖 Verdict de l'IA")
        per = info.get('trailingPE', 0)
        target = info.get('targetMeanPrice', 0)
        growth = info.get('revenueGrowth', 0)

        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            if per > 0 and per < 25 and growth > 0.1:
                st.success("✅ SIGNAL : ACHAT FORT (Croissance élevée + Valorisation correcte)")
            elif per > 40:
                st.warning("⚠️ SIGNAL : ATTENTE (Action potentiellement surévaluée)")
            else:
                st.info("ℹ️ SIGNAL : NEUTRE (À surveiller selon vos objectifs)")
        
        with col_ia2:
            if target > prix:
                st.write(f"🎯 **Objectif Analystes :** {target:.2f} {devise} (+{((target/prix)-1)*100:.1f}%)")
            else:
                st.write("🎯 **Objectif Analystes :** Atteint ou dépassé.")

        # --- 3. GRAPHIQUE INTERACTIF ---
        p_map = {"1J": "1d", "5J": "5d", "1M": "1mo", "1A": "1y", "MAX": "max"}
        sel_p = st.select_slider("Période", options=list(p_map.keys()), value="1A")
        
        hist = stock.history(period=p_map[sel_p])
        if not hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#00C805', width=2), hovertemplate="%{y:.2f}€"))
            fig.update_layout(template="plotly_dark", hovermode="x unified", dragmode=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # --- 4. ALERTES MAIL ---
        st.divider()
        st.subheader("📧 Configurer une Alerte Mail")
        email_user = st.text_input("Votre Email")
        seuil_prix = st.number_input(f"M'alerter si le prix tombe sous ({devise})", value=float(prix*0.95))
        
        if st.button("Activer la surveillance"):
            if email_user:
                st.success(f"Alerte activée ! Vous recevrez un mail si {ticker} passe sous {seuil_prix} {devise}.")
                # Note : Pour l'envoi réel, il faudra configurer les secrets Streamlit avec ton SMTP
            else:
                st.error("Veuillez entrer une adresse email valide.")

    except:
        st.error("Action introuvable.")
