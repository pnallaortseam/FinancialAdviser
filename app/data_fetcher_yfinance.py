
import os
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import glob
from config  import settings
from env import import_my_env
import yfinance as yf

import_my_env()
# Constants
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
# TODAY = datetime.today().strftime("%d-%m-%y")
# DATA_DIR = Path("./stocks_data")
# DATA_DIR.mkdir(exist_ok=True)

def create_dir():
    settings.DATA_DIR.mkdir(exist_ok=True)
    settings.OHLC_DIR.mkdir(exist_ok=True)
    settings.FUNDMENTALS_DIR.mkdir(exist_ok=True)
    settings.NEWS_DIR.mkdir(exist_ok=True)
    # settings.INCOME_STATEMENT_DIR.mkdir(exist_ok=True)
    # settings.BALANCESHEET_DIR.mkdir(exist_ok=True)
    # settings.CASHFLOW_DIR.mkdir(exist_ok=True)

def fetch_ohlc(symbol: str) -> str:
    # Set date for output filenames
    # date_str = datetime.today().strftime('%d-%m-%y')

    # Ensure target folder exists
    output_dir = f"stocks_data/OHLC"
    os.makedirs(output_dir, exist_ok=True)

    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="100d", interval="1d")  # last 100 trading days

        if not df.empty:
            df.reset_index(inplace=True)  # move Date from index to column
            # filename = f"{symbol}_OHLC_{date_str}.csv"
            # file_path = os.path.join(output_dir, filename)
            # df.to_csv(file_path, index=False)
            
            old_files = glob.glob(str(settings.OHLC_DIR / f"{symbol}_OHLC_*.csv"))
            for f in old_files:
                os.remove(f)

            df.to_csv(settings.OHLC_DIR / f"{symbol}_OHLC_{settings.TODAY}.csv", index=False)
        
            #print(f"Saved: {settings.OHLC_DIR / f"{symbol}_OHLC_{settings.TODAY}.csv"}") #pring file path
            return "OK"
        else:
            return (f"No data for: {symbol}")
    except Exception as e:
        return f"Error fetching {symbol}: {e}"

def fetch_fundamentals(symbol: str) -> str:
    # Fields to extract
    desired_keys = [
        'longName', 'sector', 'industry', 'marketCap', 'forwardPE', 'trailingPE',
        'priceToBook', 'bookValue', 'dividendYield', 'beta', 'returnOnEquity',
        'grossMargins', 'profitMargins', 'revenueGrowth', 'earningsGrowth',
        'totalRevenue', 'ebitda', 'earningsQuarterlyGrowth'
    ]

    # Fetch and save data
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        if info:
            fundamentals = {key: info.get(key, None) for key in desired_keys}
            df = pd.DataFrame([fundamentals])
            # filename = os.path.join(output_dir, f"{symbol}_fundamentals_{date_str}.csv")
            # df.to_csv(filename, index=False, encoding='utf-8')
            
            old_files = glob.glob(str(settings.FUNDMENTALS_DIR / f"{symbol}_fundamentals_*.csv"))
            for f in old_files:
                os.remove(f)

            df.to_csv(settings.FUNDMENTALS_DIR / f"{symbol}_fundamentals_{settings.TODAY}.csv", index=False)
            #print(f"Saved: {settings.FUNDMENTALS_DIR / f"{symbol}_fundamentals_{settings.TODAY}.csv"}") #print file name
            return "OK"
        else:
            return f"No fundamental info for: {symbol}"

    except Exception as e:
        return f"Error processing {symbol}: {e}"

def fetch_news(symbol: str) -> str:
    # Iterate over all stocks and save news
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        news = ticker.news

        news_data = []
        for item in news:
            content = item.get("content", {})
            canonical = content.get("canonicalUrl", "")
            url = canonical.get("url") if isinstance(canonical, dict) else canonical

            news_data.append({
                "title": content.get("title", ""),
                "summary": content.get("summary", ""),
                "pubDate": content.get("pubDate", ""),
                "url": url
            })

        if news_data:
            df = pd.DataFrame(news_data)
            # filename = os.path.join(output_dir, f"{symbol}_news_{date_str}.csv")
            # df.to_csv(filename, index=False, encoding="utf-8")

            old_files = glob.glob(str(settings.NEWS_DIR / f"{symbol}_news_*.csv"))
            for f in old_files:
                os.remove(f)

            df.to_csv(settings.NEWS_DIR / f"{symbol}_news_{settings.TODAY}.csv", index=False)
            #print(f"Saved: {settings.DATA_DIR / f"{symbol}_news_{settings.TODAY}.csv"}")
            return "OK"
        else:
            print(f"No news found for: {symbol}")

    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")    

def fetch_and_save_all_stocks(stock_list=None) -> dict:
    #Create directory structure for saving CSV files
    create_dir()
    
    symbols = stock_list or settings.INDEX_STOCKS
    results = {}
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        ohlc         = fetch_ohlc(symbol)
        fundamentals = fetch_fundamentals(symbol)
        news         = fetch_news(symbol)
        results[symbol] = {
            "ohlc": ohlc,
            "fundamentals": fundamentals,
            "news": news
        }
    return results

fetch_and_save_all_stocks()