
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import httpx
import streamlit as st
#import requests
from fpdf import FPDF
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from app.env import import_my_env

import_my_env()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

def call_backend(user_inputs):
    try:
        with httpx.Client(timeout=60) as client:
            #response = client.post("http://127.0.0.1:8000/recommend", json=user_inputs)
            response = requests.post("http://backend:8000/recommend", json=user_inputs)
            return response
    except httpx.RequestError as e:
        st.error(f"Request failed: {e}")
        return None


st.set_page_config(page_title="Financial Adviser", layout="wide")


st.markdown("""<style>
.chat-box, .advice-box {
    max-height: 400px;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #ccc;
    background-color: #fafafa;
    border-radius: 6px;
}
</style>""", unsafe_allow_html=True)


st.title("💰 Intelligent Financial Adviser")

#st.markdown("Welcome! Please fill out your financial profile below:")
st.markdown("📈 **Welcome to Financial Adviser!** \n\
             We're excited to have you on board. Your journey to smarter, more personalized investing starts here. \n\
             🚀 We'll begin by gathering a few details about your financial information, risk tolerance, and interests. \n\
             This helps us tailor stock insights and strategies that *fit you perfectly*. \n\
             **Ready to unlock your investment potential? Let’s get started! 💼** \n")

def generate_advice_pdf(advice_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Stock Advice Summary", ln=True, align="C")
    for k, v in advice_data.items():
        text = f"{k}:\n{v if isinstance(v, str) else json.dumps(v, indent=2)}"
        for line in text.split("\n"):
            pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S").encode("latin1")

# Layout: left column for inputs, right column for advice + chat
col1, col2 = st.columns([1, 2])

# --- Inputs (Left Side) ---
with col1:

    # Define inputs
    age = st.number_input("🎂 Your age:", min_value=18, max_value=100)
    monthly_income = st.number_input("💸 Monthly income (INR):", min_value=1000.0)
    monthly_expenses = st.number_input("🧾 Monthly expenses (INR):", min_value=0.0)
    monthly_investment = st.number_input("📈 Monthly investment (INR):", min_value=500.0)
    annual_extra_investment = st.number_input("🎁 Annual extra investment (INR):", min_value=0.0)
    current_savings = st.number_input("🏦 Current savings (INR):", min_value=0.0)
    risk_percent = st.slider("⚖️ Risk tolerance (0-100%)", 0, 100, 50)
    years = st.slider("📆 Investment horizon (years)", 1, 20, 5)
    expected_returns_percent = st.slider("📊 Expected annual returns (%)", 1, 20, 10)
    num_dependents = st.number_input("👨‍👩‍👧‍👦 Number of dependents:", min_value=0, max_value=10)

    investment_type = st.selectbox("🧭 Investment style:",
                                ["Aggressive 🐯", "Moderate 🦉", "Slow 🐢"])
    investor_knowledge = st.selectbox("📚 Investor knowledge level:",
                                    ["Beginner 🐣", "Intermediate 🧑‍💻", "Expert 🧠"])

    sector_list = [
            "Automobile and Auto Components", "Capital Goods", "Chemicals", "Construction",
            "Construction Materials", "Consumer Durables", "Consumer Services", "Diversified",
            "Fast Moving Consumer Goods", "Financial Services", "Forest Materials", "Healthcare",
            "Information Technology", "Media Entertainment & Publication", "Metals & Mining",
            "Oil Gas & Consumable Fuels", "Power", "Realty", "Services", "Telecommunication", "Textiles"
    ]
    interested_sectors = st.multiselect("🏭 Which sectors are you interested in? (Select any or leave blank)", sector_list)

    has_health_insurance = st.radio("🩺 Do you have health insurance?", ["yes", "no"]) == "yes"
    has_emergency_fund = st.radio("🚨 Do you have an emergency fund?", ["yes", "no"]) == "yes"


# --- Output + Chat (Right Side) ---
with col2:

    # Submit button
    if st.button("📤 Get Stock Advice"):
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
            "investment_type": investment_type.split()[0],  # remove emoji
            "investor_knowledge": investor_knowledge.split()[0],
            "interested_sectors": interested_sectors,
            "has_health_insurance": has_health_insurance,
            "has_emergency_fund": has_emergency_fund,
        }

        #st.subheader("📡 Sending to backend...")
        with st.spinner("⏳ Analyzing your financial profile. This may take a few moments..."):
            try:
                #response = requests.post("http://127.0.0.1:8000/recommend", json=user_data)
                response = call_backend(user_data)
                if response.status_code == 200:
                    advice_data = response.json()
                    st.session_state["advice_data"] = advice_data
                    st.session_state["final_advice"] = advice_data.get("advice", "")
                    st.success("✅ Advice received!")
                    # st.markdown("### 📈 Your Stock Recommendation")
                    # st.markdown(advice)
                else:
                    st.error(f"❌ Backend error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Request failed: {e}")

    if "advice_data" in st.session_state:
        st.markdown("### 📈 Your Stock Recommendation")
        with st.container():
            st.markdown("#### Backend Advice")
            st.markdown(f"<div class=\"advice-box\">{st.session_state['advice_data'].get('advice', 'No advice available.')}</div>", unsafe_allow_html=True)

        pdf_bytes = generate_advice_pdf(st.session_state["advice_data"])
        st.download_button("📥 Download Advice as PDF", pdf_bytes, "advice_report.pdf", mime="application/pdf")
        
        # 💬 Chat interface below advice
        if "final_advice" in st.session_state:
            st.markdown("---")
            st.markdown("### 💬 Ask questions about the stock advice")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

            user_msg = st.chat_input("Ask a question related to your stock advice...")

            if user_msg:
                # with st.chat_message("user"):
                #     st.markdown(user_msg)
                full_prompt = f"""You are a helpful financial assistant.\n\n\
                                Here is the user's financial profile and backend-generated recommendation:\n\
                                {json.dumps(st.session_state["advice_data"], indent=2)}\n\nNow the user asks:\n\
                                {user_msg} \n\n\
                                Please provide a clear, factual, and helpful response."""

                try:
                    response = llm.invoke(full_prompt).content.strip()
                except Exception as e:
                    response = f"⚠️ Failed to fetch LLM response: {e}"

                # with st.chat_message("assistant"):
                #     st.markdown(response)

                st.session_state.chat_history.append((user_msg, response))

                st.markdown("#### Chat History")
                st.markdown("<div class=\"chat-box\">", unsafe_allow_html=True)
                
            for msg, resp in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.markdown(msg)
                with st.chat_message("assistant"):
                    st.markdown(resp)
                    st.markdown("</div>", unsafe_allow_html=True)
