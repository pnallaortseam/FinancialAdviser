
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.stock_analysis import summarize_stock_insights
from app.rank_top_stocks import rank_top_stocks
from app.llm_prompt import get_final_stock_advice

app = FastAPI()

class UserProfile(BaseModel):
    age: int
    monthly_income: float
    monthly_expenses: float
    monthly_investment: float
    annual_extra_investment: float
    current_savings: float
    risk_percent: int
    years: int
    expected_returns_percent: int
    num_dependents: int
    has_health_insurance: bool
    has_emergency_fund: bool
    investment_type: str
    interested_sectors: List[str]
    investor_knowledge: str

@app.post("/recommend")
async def recommend(user: UserProfile):
    # Validation
    errors = []
    if user.monthly_expenses > user.monthly_income:
        errors.append("Monthly expenses cannot exceed income.")
    disposable_income = user.monthly_income - user.monthly_expenses
    if disposable_income <= 0:
        errors.append("Disposable income is zero or negative.")
    elif user.monthly_investment > disposable_income:
        errors.append("Investment exceeds disposable income.")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    user_dict = user.dict()
    user_dict["investment_amount"] = user.monthly_investment * 12 * user.years + user.annual_extra_investment * user.years
    top10 = rank_top_stocks(user_dict)[:10]
    summaries = {symbol.upper(): summarize_stock_insights(symbol) for symbol, _ in top10}
    advice, updated_summaries = get_final_stock_advice(user_dict, summaries)

    return {
        "user_profile": user_dict,
        "top_stocks": [symbol for symbol, _ in top10],
        "advice": advice,
        "growth_data": updated_summaries
    }
