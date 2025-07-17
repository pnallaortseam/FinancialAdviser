import pandas as pd
from datetime import datetime
from transformers import pipeline
#from app.config import settings
from data_cache import fundamentals_data, ohlc_data, news_data

sentiment_model = pipeline("sentiment-analysis",
                           model="distilbert-base-uncased-finetuned-sst-2-english")

def get_sentiment_from_news(df: pd.DataFrame) -> tuple[float, list[str]]:
    #print("### get_sentiment_from_news")
    headlines = df["title"].dropna().tolist()[:3]
    if not headlines:
        return 0.0, []
    results = sentiment_model(headlines)
    score = sum(r["score"] if r["label"] == "POSITIVE" else -r["score"] for r in results)
    return score / len(results), headlines

def get_company_intro(symbol: str) -> str:
    try:
        df = fundamentals_data[symbol]
        name = df.get("longName", [symbol])[0]
        sector = df.get("sector", ["Unknown"])[0]
        industry = df.get("industry", [""])[0]
        return f"{name} is a major company in the {sector} sector, operating in the {industry} industry."
    except Exception:
        return f"{symbol} is a listed company on the NSE."

def get_recent_movement_summary(symbol: str) -> str:
    try:
        df = ohlc_data[symbol].copy()
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        df = df.sort_values("Date")
        start, end = df["Close"].iloc[0], df["Close"].iloc[-1]
        pct_change = (end - start) / start * 100
        return f"From {df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()}, {symbol}'s stock price changed by {pct_change:.2f}%."
    except Exception:
        return f"Recent price movement data for {symbol} is unavailable."

def get_top_news_titles(symbol: str) -> list:
    try:
        return news_data[symbol]["title"].fillna("").tolist()[:3]
    except Exception:
        return []

def get_financial_highlights(symbol: str) -> list:
    try:
        df = fundamentals_data[symbol]
        lines = []
        for col in ["marketCap", "trailingPE", "priceToBook", "bookValue", "dividendYield", "returnOnEquity"]:
            if col in df.columns:
                val = df[col].iloc[0]
                lines.append(f"{col}: {val}")
        return lines
    except Exception:
        return []

def summarize_stock_insights(symbol: str) -> dict:
    return {
        "intro": get_company_intro(symbol),
        "movement": get_recent_movement_summary(symbol),
        "headlines": get_top_news_titles(symbol),
        "financials": get_financial_highlights(symbol),
        "asof": datetime.today().strftime("%Y-%m-%d")
    }
