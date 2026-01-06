import os
import requests
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__)

# --- DATA ENGINE ---
def get_sp500_data():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        tickers = pd.read_html(response.text)[0]['Symbol'].str.replace('.', '-').tolist()
        
        data = yf.download(tickers, period="2d", group_by='ticker', progress=False)
        ranked_list = []
        for t in tickers:
            try:
                df = data[t]
                if df.empty: continue
                cp, pc = df['Close'].iloc[-1], df['Close'].iloc[-2]
                pct = ((cp - pc) / pc) * 100
                
                color = "#00FF88" if pct > 0 else "#FF0055"
                sig = "⚡ BUY" if pct > 0.3 else "💀 SELL" if pct < -0.3 else "🌑 NEUTRAL"
                
                ranked_list.append({"ticker": t, "price": f"${cp:,.2f}", "change": round(pct, 2), "signal": sig, "color": color})
            except: continue
        return sorted(ranked_list, key=lambda x: x['change'], reverse=True)
    except: return []

# --- ROUTES ---
@app.route('/')
def home():
    stocks = get_sp500_data()
    return render_template('index.html', stocks=stocks)

@app.route('/privacy')
def privacy(): return render_template('privacy.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/ads.txt')
def ads_txt():
    return "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
