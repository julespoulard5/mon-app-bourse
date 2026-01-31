import yfinance as yf
import requests
import time

# --- CONFIGURATION ---
TOKEN_TELEGRAM = "VOTRE_TOKEN_TELEGRAM"
CHAT_ID = "VOTRE_CHAT_ID"
WATCHLIST = ["AAPL", "TSLA", "MC.PA", "ASML", "NVDA"] # Ajoutez vos actions ici

def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analyser_opportunite(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    prix_actuel = info.get('currentPrice')
    cible_basse = info.get('targetLowPrice')
    roe = info.get('returnOnEquity', 0)
    per = info.get('trailingPE', 100)
    nom = info.get('longName', ticker)

    # Condition de "Solde" : Prix sous la cible basse des analystes
    if prix_actuel and cible_basse and prix_actuel <= cible_basse:
        
        # LOGIQUE IA : Est-ce un bon achat ?
        # Une entreprise solide a généralement un ROE > 12% et un PER raisonnable
        if roe > 0.12 and per < 25:
            score_ia = "✅ OPPORTUNITÉ FORTE (Fondamentaux solides)"
            raison = f"L'entreprise est très rentable (ROE: {roe*100:.1f}%) et le prix est bradé par rapport aux prévisions."
        else:
            score_ia = "⚠️ ATTENTION (Risque élevé)"
            raison = f"Le prix est bas, mais la rentabilité est faible (ROE: {roe*100:.1f}%). Possible 'Value Trap'."

        message = (
            f"🚨 *ALERTE SOLDE : {nom} ({ticker})*\n\n"
            f"💰 Prix Actuel : {prix_actuel}$\n"
            f"🎯 Cible Basse : {cible_basse}$\n"
            f"📊 PER : {per}x | ROE : {roe*100:.1f}%\n\n"
            f"🤖 *Analyse IA :* {score_ia}\n"
            f"📝 *Pourquoi :* {raison}"
        )
        return message
    return None

def executer_surveillance():
    print("🚀 Bot de surveillance démarré...")
    for ticker in WATCHLIST:
        print(f"Vérification de {ticker}...")
        alerte = analyser_opportunite(ticker)
        if alerte:
            envoyer_alerte(alerte)
    print("✅ Vérification terminée.")

# Le bot vérifie toutes les 4 heures (14400 secondes)
while True:
    executer_surveillance()
    time.sleep(14400) 
