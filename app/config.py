from pydantic_settings import BaseSettings
from datetime import datetime
from pathlib import Path
import pandas as pd

class Settings(BaseSettings):
    DATA_DIR: Path = Path("./stocks_data")
    OHLC_DIR: Path = DATA_DIR / "OHLC"
    FUNDMENTALS_DIR: Path = DATA_DIR / "Fundamentals"
    NEWS_DIR: Path = DATA_DIR / "news"
    TODAY: str = datetime.today().strftime("%d-%m-%y")
    INDEX_STOCKS: list[str] = []
    NUM_SCREENED_STOCKS: int = 20 #Number of stocks to shortlist from full list based on user input

    class Config:
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dynamically populate INDEX_STOCKS from CSV
        csv_path = Path("./stocks_data/nifty_500_lst.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if "Symbol" in df.columns:
                self.INDEX_STOCKS = df["Symbol"].dropna().astype(str).str.upper().tolist()


settings = Settings()