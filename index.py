import os
import requests
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='../templates')

# --- DATA ENGINE ---
def get_full_sp500_ranked():
    # Fetching S&P 500 Tickers from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # Using the first table on the page
    tickers = pd.read_html(response.text)[0]['Symbol'].str.replace('.', '-').tolist()
    
    # Downloading 2 days of data for all tickers at once (Batching)
    data = yf.download(tickers, period="2d", group_by='ticker', progress=False)
    
    ranked_list = []
    for t in tickers:
        try:
            df = data[t]
            if df.empty: continue
            
            # Get latest and previous close prices
            cp, pc = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((cp - pc) / pc) * 100
            
            # Logic for signals (Neon Colors)
            if pct > 2.0: sig, color = "⚡ STRONG BUY", "#00FF88"
            elif pct > 0.3: sig, color = "📈 BUY", "#00FF88"
            elif pct < -2.0: sig, color = "💀 STRONG SELL", "#FF0055"
            elif pct < -0.3: sig, color = "📉 SELL", "#FF0055"
            else: sig, color = "🌑 NEUTRAL", "#30363D"
            
            ranked_list.append({
                "ticker": t, 
                "price": f"${cp:,.2f}", 
                "change": round(pct, 2), 
                "signal": sig,
                "color": color
            })
        except:
            continue
            
    # Return sorted by performance
    return sorted(ranked_list, key=lambda x: x['change'], reverse=True)

# --- ROUTES ---
@app.route('/')
def home():
    stocks = get_full_sp500_ranked()
    return render_template('index.html', stocks=stocks)

# Legal Pages for AdSense Approval
@app.route('/privacy')
def privacy(): return render_template('privacy.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/ads.txt')
def ads_txt():
    # Replace the pub ID with your actual Google Publisher ID
    return "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

# Necessary for Vercel
app.debug = True
