import requests
import time
import os
from datetime import datetime, timezone
import ccxt

# ====== CONFIGURATION ======
TELEGRAM_TOKEN = os.getenv("7567841237:AAGgfQf1WQJl-CbMV688JME7ax1PqQ-anx8")
CHAT_ID = os.getenv("881040918693")
INTERVAL_HOURS = int(os.getenv("INTERVAL_HOURS", 4))  # Default 4 hour

# ====== TELEGRAM FUNCTIONS ======
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram error:", e)

# ====== EXCHANGES ======
exchanges = [
    ccxt.binance(),
    ccxt.bybit(),
    ccxt.okx(),
]

# ====== LOGIC FUNCTION ======
def check_halftrend_signals():
    results = []
    for ex in exchanges:
        try:
            markets = ex.load_markets()
            for symbol in list(markets.keys())[:50]:  # limit to first 50 for speed
                try:
                    ohlcv = ex.fetch_ohlcv(symbol, timeframe=f"{INTERVAL_HOURS}h", limit=20)
                    closes = [c[4] for c in ohlcv]
                    if closes[-1] > closes[-2]:  # simple uptrend logic
                        results.append(f"📈 {ex.id.upper()} - {symbol} UP")
                    elif closes[-1] < closes[-2]:
                        results.append(f"📉 {ex.id.upper()} - {symbol} DOWN")
                except:
                    continue
        except Exception as e:
            print(f"Error loading markets for {ex.id}: {e}")
    return results

# ====== MAIN LOOP ======
if __name__ == "__main__":
    send_telegram("✅ HalfTrend Scanner started successfully on Render!")

    while True:
        try:
            print(f"⏰ Checking {INTERVAL_HOURS}h trends at {datetime.now(timezone.utc)}")
            signals = check_halftrend_signals()

            if signals:
                send_telegram("🚨 Trend Signals:\n" + "\n".join(signals))
            else:
                send_telegram("😴 No strong signals this cycle.")

        except Exception as e:
            send_telegram(f"❌ Error: {e}")
            print("Main loop error:", e)

        time.sleep(INTERVAL_HOURS * 3600)
