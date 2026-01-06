import os
import requests
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__)

@app.cache_data = {} # Simple logic to store data for an hour

def get_full_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tickers = pd.read_html(response.text)[0]['Symbol'].str.replace('.', '-').tolist()
    
    # Download data for all tickers
    data = yf.download(tickers, period="2d", group_by='ticker', progress=False)
    
    ranked_list = []
    for t in tickers:
        try:
            df = data[t]
            if df.empty: continue
            cp, pc = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((cp - pc) / pc) * 100
            
            if pct > 2.0: sig, color = "⚡ STRONG BUY", "#00FF88"
            elif pct > 0.3: sig, color = "📈 BUY", "#00FF88"
            elif pct < -2.0: sig, color = "💀 STRONG SELL", "#FF0055"
            elif pct < -0.3: sig, color = "📉 SELL", "#FF0055"
            else: sig, color = "🌑 NEUTRAL", "#30363d"
            
            ranked_list.append({
                "ticker": t, 
                "price": f"${cp:,.2f}", 
                "change": round(pct, 2), 
                "signal": sig,
                "color": color
            })
        except: continue
    return sorted(ranked_list, key=lambda x: x['change'], reverse=True)

@app.route('/')
def home():
    stocks = get_full_sp500()
    return render_template('index.html', stocks=stocks)

@app.route('/ads.txt')
def ads_txt():
    # REQUIRED for Google AdSense verification
    return "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
