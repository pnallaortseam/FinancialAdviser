
import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
import re
#from app.investment_growth_chart import plot_growth_using_llm_output

def run_streamlit_ui():
    st.set_page_config(page_title="AI Stock Advisor", layout="wide")
    st.title("AI Stock Advisor")

    with st.form("user_profile"):
        age = st.number_input("Age", 18, 100, 35)
        monthly_income = st.number_input("Monthly Income (INR)", value=100000)
        monthly_expenses = st.number_input("Monthly Expenses (INR)", value=50000)
        monthly_investment = st.number_input("Monthly Investment (INR)", value=20000)
        annual_extra_investment = st.number_input("Annual Extra Investment (INR)", value=50000)
        current_savings = st.number_input("Current Savings (INR)", value=500000)
        risk_percent = st.slider("Risk Tolerance (%)", 0, 100, 10)
        years = st.number_input("Investment Horizon (Years)", value=10)
        expected_returns_percent = st.slider("Expected Returns (%)", 1, 20, 12)
        num_dependents = st.number_input("Number of Dependents", value=1)
        investment_type = st.selectbox("Investment Style", ["Aggressive", "Moderate", "Slow"])
        investor_knowledge = st.selectbox("Investor Knowledge Level", ["Beginner", "Intermediate", "Expert"])
        interested_sectors = st.multiselect(
            "Interested Sectors",
            [
                "Automobile and Auto Components", "Capital Goods", "Chemicals", "Construction",
                "Construction Materials", "Consumer Durables", "Consumer Services", "Diversified",
                "Fast Moving Consumer Goods", "Financial Services", "Forest Materials", "Healthcare",
                "Information Technology", "Media Entertainment & Publication", "Metals & Mining",
                "Oil Gas & Consumable Fuels", "Power", "Realty", "Services", "Telecommunication", "Textiles"
            ],
            default=["Information Technology"]
        )
        has_health_insurance = st.checkbox("Health Insurance", value=True)
        has_emergency_fund = st.checkbox("Emergency Fund Available", value=True)
        submitted = st.form_submit_button("Submit")

    if submitted:
        # Validation checks before API call
        if monthly_expenses > monthly_income:
            st.error("Monthly expenses cannot exceed monthly income.")
            return
        if monthly_income - monthly_expenses <= 0:
            st.error("Disposable income must be positive.")
            return
        if monthly_investment > (monthly_income - monthly_expenses):
            st.error("Monthly investment cannot exceed disposable income.")
            return

        user_data = {
            "age": age,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_investment": monthly_investment,
            "annual_extra_investment": annual_extra_investment,
            "current_savings": current_savings,
            "risk_percent": risk_percent,
            "years": years,
            "expected_returns_percent": expected_returns_percent,
            "num_dependents": num_dependents,
            "has_health_insurance": has_health_insurance,
            "has_emergency_fund": has_emergency_fund,
            "investment_type": investment_type,
            "interested_sectors": interested_sectors,
            "investor_knowledge": investor_knowledge
        }

        st.subheader("Generating the advice...")
        try:
            #res = requests.post("http://localhost:8000/recommend", json=user_data)
            res = requests.post("http://backend:8000/recommend", json=user_data)
            if res.status_code == 200:
                result = res.json()
                advice = result["advice"]
                summaries = result["growth_data"]

                st.success("Stock advice creation success")
                st.write("📋 Profile Summary")
                st.json(result["user_profile"])

                print("########### user_profile ################\n")
                print(result["user_profile"])
                
                print("########### advice ################\n")
                print(result["advice"])
                
                print("########### growth_data ################\n")
                print(result["growth_data"])
                
                print("########### top_stocks ################\n")
                print(result["top_stocks"])

                rows = []
                current_stock = None
                summary = ""
                concern = ""
                growth = 0.0
                invest = 0

                # Parce the received stock advice for structured display
                for line in advice.split("\n"):
                    line = line.strip()
                    if re.match(r"^\d+\.\s+\w+", line):
                        if current_stock:
                            risk = "High" if growth > 12 else "Medium" if growth > 8 else "Low"
                            rows.append((current_stock, summary, f"{invest}%", f"{growth:.2f}%", risk))
                        current_stock = line.split(".")[1].strip()
                        summary = ""
                        concern = ""
                        growth = 0.0
                        invest = 0
                    elif line.startswith("Summary:"):
                        summary = line.replace("Summary:", "").strip()
                    elif line.startswith("Concern:"):
                        concern = line.replace("Concern:", "").strip()
                    elif line.startswith("Growth:"):
                        try:
                            growth = float(line.replace("Growth:", "").replace("%", "").strip().rstrip("."))
                        except:
                            growth = 0.0
                    elif line.startswith("Invest:"):
                        try:
                            invest = int(line.replace("Invest:", "").replace("%", "").strip())
                        except:
                            invest = 0

                if current_stock:
                    risk = "High" if growth > 12 else "Medium" if growth > 8 else "Low"
                    rows.append((current_stock, summary, f"{invest}%", f"{growth:.2f}%", risk))

                if rows:
                    df = pd.DataFrame(rows, columns=["Stock", "Advice", "% of Investment", "Forecast Growth", "Risk"])
                    st.write("Final Advice with Growth Forecast")
                    st.dataframe(df)

                    #st.download_button("📥 Download CSV", df.to_csv(index=False), "stock_advice.csv", "text/csv")
                    #st.download_button("📥 Download Excel", df.to_excel(index=False, engine='openpyxl'), "stock_advice.xlsx")

                    # Forecast-based plotting
                    st.write("📈 Growth Simulation")
                    timeline = list(range(1, user_data["years"] * 12 + 1))
                    projections = []
                    fig, ax = plt.subplots(figsize=(10, 5))

                    for _, row in df.iterrows():
                        stock = row["Stock"]
                        invest_pct = int(row["% of Investment"].replace("%", ""))
                        growth_pct = float(row["Forecast Growth"].replace("%", "")) / 100
                        r = growth_pct / 12
                        balance = 0
                        values = []
                        for m in timeline:
                            balance = balance * (1 + r) + (user_data["monthly_investment"] * invest_pct / 100)
                            if m % 12 == 0:
                                balance += user_data["annual_extra_investment"] * invest_pct / 100
                            values.append(balance)
                        ax.plot(timeline, values, label=stock)
                        projections.append(pd.DataFrame({"Month": timeline, stock: [round(v, 2) for v in values]}))

                    ax.set_xlabel("Month")
                    ax.set_ylabel("₹ Value")
                    ax.set_title("Projected Growth by Stock")
                    ax.legend(loc="upper left", fontsize="small")
                    ax.grid(True)
                    st.pyplot(fig)

                    merged = projections[0]
                    for df_piece in projections[1:]:
                        merged = pd.merge(merged, df_piece, on="Month", how="outer")
                    st.download_button("Download Monthly Projection", merged.to_csv(index=False), "monthly_growth_projection.csv", "text/csv")
                else:
                    st.text(advice)

            else:
                st.error("API Error")
        except Exception as e:
            st.error(f"API failure: {e}")

if __name__ == "__main__":
    run_streamlit_ui()

