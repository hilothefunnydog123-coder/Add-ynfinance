import os
import requests
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request

# The '../templates' tells Flask to look outside the 'api' folder for your HTML
app = Flask(__name__, template_folder='../templates')

# --- 1. DATA ENGINE (S&P 500) ---
def get_sp500_data():
    try:
        # Fetch tickers from Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        tickers = pd.read_html(response.text)[0]['Symbol'].str.replace('.', '-').tolist()
        
        # Download data for all tickers (Batching is faster for Vercel)
        data = yf.download(tickers, period="2d", group_by='ticker', progress=False)
        
        ranked_list = []
        for t in tickers:
            try:
                df = data[t]
                if df.empty: continue
                cp, pc = df['Close'].iloc[-1], df['Close'].iloc[-2]
                pct = ((cp - pc) / pc) * 100
                
                # Assign Signal and Neon Colors
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
            except: continue
        
        # Sort by best performance first
        return sorted(ranked_list, key=lambda x: x['change'], reverse=True)
    except Exception as e:
        print(f"Error: {e}")
        return []

# --- 2. MAIN ROUTES ---
@app.route('/')
def home():
    stocks = get_sp500_data()
    return render_template('index.html', stocks=stocks)

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form.get('ticker', 'TSLA').upper()
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return render_template('index.html', result=ticker, price=f"{price:.2f}")
    except:
        return render_template('index.html', error="Invalid Symbol")

# --- 3. LEGAL PAGES (Required for AdSense) ---
@app.route('/privacy')
def privacy(): 
    return render_template('privacy.html')

@app.route('/about')
def about(): 
    return render_template('about.html')

@app.route('/contact')
def contact(): 
    return render_template('contact.html')

@app.route('/ads.txt')
def ads_txt():
    # Google will look here to verify your ownership
    # IMPORTANT: Replace 'pub-0000000000000000' with your real ID later
    return "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

# Vercel needs this to handle the app object
app.debug = True
