
import re
import json
import httpx
import chainlit as cl
from langchain_google_genai import ChatGoogleGenerativeAI
from env import import_my_env

import_my_env()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

sector_list = [
    "Automobile and Auto Components", "Capital Goods", "Chemicals", "Construction",
    "Construction Materials", "Consumer Durables", "Consumer Services", "Diversified",
    "Fast Moving Consumer Goods", "Financial Services", "Forest Materials", "Healthcare",
    "Information Technology", "Media Entertainment & Publication", "Metals & Mining",
    "Oil Gas & Consumable Fuels", "Power", "Realty", "Services", "Telecommunication", "Textiles"]

questions = [
    ("age", "What is your age? (18–100)", int, lambda x: 18 <= x <= 100),
    ("monthly_income", "What is your monthly income in INR?", float, lambda x: x >= 1000),
    ("monthly_expenses", "What are your monthly expenses in INR?", float, lambda x: x >= 0),
    ("monthly_investment", "How much do you invest monthly in INR?", float, lambda x: x >= 500),
    ("annual_extra_investment", "Any annual extra investment (INR)?", float, lambda x: x >= 0),
    ("current_savings", "How much are your current savings (INR)?", float, lambda x: x >= 0),
    ("risk_percent", "What is your risk tolerance? (0–100%)", int, lambda x: 0 <= x <= 100),
    ("years", "What is your investment horizon in years?", int, lambda x: 1 <= x <= 20),
    ("expected_returns_percent", "What returns do you expect annually? (1–20%)", int, lambda x: 1 <= x <= 20),
    ("num_dependents", "How many dependents do you have? (0–10)", int, lambda x: 0 <= x <= 10),
    ("investment_type", "What is your investment style? (Aggressive, Moderate, Slow)", str, lambda x: x in ["Aggressive", "Moderate", "Slow", \
                                                                                                            "aggressive", "moderate", "slow"]),
    ("investor_knowledge", "What is your investor knowledge level? (Beginner, Intermediate, Expert)", str, lambda x: x in ["Beginner", "Intermediate", "Expert", 
                                                                                                                           "beginner", "intermediate", "expert"]),
    ("interested_sectors", f"Which sectors are you interested in? Provide a comma-separated list from:{', '.join(sector_list)}", list, lambda x: isinstance(x, list)),
    ("has_health_insurance", "Do you have health insurance? (yes/no)", bool, lambda x: isinstance(x, bool)),
    ("has_emergency_fund", "Do you have an emergency fund? (yes/no)", bool, lambda x: isinstance(x, bool)),
]

async def display_user_inputs(user_inputs):
    formatted = "\n### **User Financial Profile**"
    formatted += "\n### **Basic Information**"
    formatted += f"\n- **Age:** {user_inputs.get('age', 'N/A')}"
    formatted += f"\n- **Dependents:** {user_inputs.get('num_dependents', 'N/A')}"
    formatted += "\n### **Financial Snapshot**"
    formatted += f"\n- **Monthly Income    :** ₹{user_inputs.get('monthly_income', 'N/A')}"
    formatted += f"\n- **Monthly Expenses  :** ₹{user_inputs.get('monthly_expenses', 'N/A')}"
    formatted += f"\n- **Monthly Investment:** ₹{user_inputs.get('monthly_investment', 'N/A')}"
    formatted += f"\n- **Annual Extra Investment:** ₹{user_inputs.get('annual_extra_investment', 'N/A')}"
    formatted += f"\n- **Current Savings:** ₹{user_inputs.get('current_savings', 'N/A')}"
    formatted += "\n### **Safety Nets**"
    hi = "✅ *Available*" if user_inputs.get("has_health_insurance") else "❌ *Not available*"
    ef = "✅ *Available*" if user_inputs.get("has_emergency_fund") else "❌ *Not available*"
    formatted += f"\n- **Health Insurance:** {hi}"
    formatted += f"\n- **Emergency Fund:** {ef}"
    formatted += "\n### **Investment Preferences**"
    sectors = user_inputs.get("interested_sectors", [])
    if isinstance(sectors, list):
        sectors = ", ".join(sectors)
    formatted += f"\n- **Interested Sectors:** {sectors if sectors else 'N/A'}"
    formatted += f"\n- **Investor Knowledge:** *{user_inputs.get('investor_knowledge', 'N/A')}*"
    formatted += f"\n- **Investment Style  :** *{user_inputs.get('investment_type', 'N/A')}*"
    formatted += f"\n- **Risk Tolerance    :** *{user_inputs.get('risk_percent', 'N/A')}%*"
    formatted += f"\n- **Investment Horizon:** *{user_inputs.get('years', 'N/A')} years*"
    formatted += f"\n- **Expected Annual Returns:** *{user_inputs.get('expected_returns_percent', 'N/A')}%*"   

    await cl.Message(content=formatted).send()

def convert_input(value, _type):
    if _type == bool:
        return value.lower() in ["yes", "true", "1"]
    # if _type == list:
    #     selected = [v.strip().lower() for v in value.split(",")]
    #     return [s for s in sector_list if s.lower() in selected or any(s.lower() == part for part in selected)]
    if _type == list:
        selected = [v.strip().lower() for v in value.split(",")]
        valid = [s for s in sector_list if s.lower() in selected]
        return valid  # this will return [] if input was invalid, which validator will catch

    return _type(value)

def build_user_data_prompt(data):
    prompt = "Generate a JSON object using the following conversation.\n"
    for key, question, _type, _ in questions:
        if key in data:
            prompt += f"{question}\nAnswer: {data[key]}\n"
    prompt += "\nReturn JSON in the format:\n{...all fields as keys...}"
    prompt += """\nuser_data = {
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
        }"""
    return prompt

@cl.on_chat_start
async def start():
    cl.user_session.set("user_inputs", {})
    cl.user_session.set("current_index", 0)
    cl.user_session.set("modify", None)
    cl.user_session.set("modify_index", 0)
    cl.user_session.set("awaiting_value", False)
    await cl.Message(content="Welcome to Financial Adviser! Let's gather some information to personalize your stock advice.").send()
    await ask_next_question()

async def ask_next_question():
    try:
        user_inputs = cl.user_session.get("user_inputs")
        current_index = cl.user_session.get("current_index")
        while current_index < len(questions):
            key, qtext, _type, validator = questions[current_index]
            if key not in user_inputs:
                await cl.Message(content=qtext).send()
                return
            current_index += 1

        user_inputs = await enrich_inputs_with_llm(user_inputs)

        cl.user_session.set("user_inputs", user_inputs)

        # Validation before backend call
        validation_errors = validate_user_inputs(user_inputs)
        if validation_errors:
            error_message = "❌ **Validation errors detected:**\n\n"
            for err in validation_errors:
                error_message += f"- {err}\n"

            await cl.Message(content=error_message).send()
            await start()  # Restart input flow from the beginning
            return

        print(f"##### Backend user_inputs:{user_inputs}")
        await cl.Message(content="✅ All inputs collected. Sending to backend...").send()
        
        r = await call_backend(user_inputs)
            
        print(f"##### Backend response:{r}")
        if r.status_code == 200:
            await cl.Message(content="📈 Recommendation Result:").send()
            await cl.Message(content=r.json()["advice"]).send()
            await cl.Message(content="Enter \n 'Modify' -> To change inputs \n \
                                               'Done' -> To start over \n \
                                               'Show User inputs' -> To display user inputs").send()
        else:
            await cl.Message(content=f"❌ Backend error: {r.status_code}").send()

    except (httpx.RequestError, Exception) as e:
        await cl.Message(content=f"❌ Backend is unreachable or failed: {e}. Restarting session...").send()
        await start()


@cl.on_message
async def handle_msg(msg: cl.Message):
    content = msg.content.strip()
    user_inputs = cl.user_session.get("user_inputs")

    if content.lower() == "done":
        await start()
        return
    
    if content.lower() == "show user inputs":
        await display_user_inputs(user_inputs)
        await cl.Message(content="Enter \n 'Modify' -> To change inputs \n \
                                           'Done' -> To start over \n \
                                           'Show User inputs' -> To display user inputs").send()
        return

    if content.lower() == "modify":
        await cl.Message(content="Please provide the inputs you want to modify from:\
                         `interested_sectors`, `risk_percent`, `years`, `expected_returns_percent`, `investment_type`").send()
        cl.user_session.set("awaiting_modification_list", True)
        return

    if cl.user_session.get("awaiting_modification_list"):
        if not await handle_modify_trigger(content):
            return
        # Await next input to process

    if cl.user_session.get("modify") is not None:
        if await process_modification(content, user_inputs):
            return

    current_index = cl.user_session.get("current_index")
    if current_index >= len(questions):
        await cl.Message(content="✅ All inputs collected.\n \
                                  Enter \n 'Modify' -> To change inputs \n \
                                           'Done' -> To start over \n \
                                           'Show User inputs' -> To display user inputs").send()
        return

    key, question, _type, validator = questions[current_index]
    try:
        value = convert_input(content, _type)
        if not validator(value):
            raise ValueError()
        user_inputs[key] = value
        cl.user_session.set("user_inputs", user_inputs)
        cl.user_session.set("current_index", current_index + 1)
        await ask_next_question()
    except:
        await cl.Message(content="❌ Invalid input. Please try again.").send()
        await cl.Message(content=question).send()


def validate_user_inputs(user_inputs):
    errors = []
    for key, _, _type, validator in questions:
        #print(f"key:{key}")
        if key not in user_inputs:
            errors.append(f"Missing input: {key}")
        else:
            try:
                value = user_inputs[key]
                #print(f">>>>>>value:{value} validator(value):{validator(value)}")
                if isinstance(value, str) and _type != str:
                    value = convert_input(value, _type)
                    user_inputs[key] = value
                if not validator(value):
                    errors.append(f"Invalid value for {key}: {value}")
            except Exception:
                errors.append(f"Validation failed for {key}: {user_inputs[key]}")
    # Cross-field validations
    if all(k in user_inputs for k in ["monthly_income", "monthly_expenses", "monthly_investment"]):
        income = user_inputs["monthly_income"]
        expenses = user_inputs["monthly_expenses"]
        investment = user_inputs["monthly_investment"]
        if investment > (income - expenses):
            errors.append("Monthly investment cannot exceed (monthly income - monthly expenses).")
    if "monthly_income" in user_inputs and "monthly_expenses" in user_inputs:
        if user_inputs["monthly_expenses"] > user_inputs["monthly_income"]:
            errors.append("Monthly expenses cannot exceed monthly income.")
    return errors


async def validate_and_continue(user_inputs):
    validation_errors = validate_user_inputs(user_inputs)
    if validation_errors:
        error_message = "❌ **Validation errors detected:**"
        for err in validation_errors:
            error_message += f"- {err}"
        await cl.Message(content=error_message).send()
        await start()
        return False
    return True

async def call_backend(user_inputs):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post("http://backend:8000/recommend", json=user_inputs)
        #response = await client.post("http://127.0.0.1:8000/recommend", json=user_inputs)
    return response


async def handle_modify_trigger(msg_content):
    modifiable_keys = ["interested_sectors", "risk_percent", "years", "expected_returns_percent", "investment_type"]
    requested_keys = [k.strip().lower() for k in msg_content.lower().split(",") if k.strip().lower() in modifiable_keys]
    if not requested_keys:
        await cl.Message(content="❌ Invalid fields. Please choose from: " + ", ".join(modifiable_keys)).send()
        return False
    cl.user_session.set("modify", requested_keys)
    cl.user_session.set("modify_index", 0)
    cl.user_session.set("awaiting_value", False)
    cl.user_session.set("awaiting_modification_list", False)
    return True

async def enrich_inputs_with_llm(user_inputs):
    prompt = build_user_data_prompt(user_inputs)
    response = llm.invoke(prompt)
    raw_output = response.content.strip()
    clean_output = re.sub(r"^```json|```$", "", raw_output, flags=re.MULTILINE).strip()
    parsed = json.loads(clean_output)
    user_inputs.update(parsed)
    cl.user_session.set("user_inputs", user_inputs)
    return user_inputs

async def process_modification(content, user_inputs):
    modify_keys = cl.user_session.get("modify")
    modify_index = cl.user_session.get("modify_index", 0)
    awaiting_value = cl.user_session.get("awaiting_value", False)

    if awaiting_value and modify_index < len(modify_keys):
        mod_key = modify_keys[modify_index]
        for key, question, _type, validator in questions:
            if key == mod_key:
                try:
                    value = convert_input(content, _type)
                    if not validator(value):
                        raise ValueError()
                    user_inputs[key] = value.title() if isinstance(value, str) else value
                    cl.user_session.set("user_inputs", user_inputs)
                    cl.user_session.set("modify_index", modify_index + 1)
                    cl.user_session.set("awaiting_value", False)
                except:
                    await cl.Message(content="❌ Invalid input. Please try again.").send()
                    await cl.Message(content=question).send()
                    return True

    # still in modification flow
    if cl.user_session.get("modify_index", 0) < len(modify_keys):
        mod_key = modify_keys[cl.user_session.get("modify_index")]
        for key, question, *_ in questions:
            if key == mod_key:
                cl.user_session.set("awaiting_value", True)
                await cl.Message(content=f"🔁 Let's update: {question}").send()
                return True
    else:
        cl.user_session.set("modify", None)
        cl.user_session.set("modify_index", 0)
        cl.user_session.set("awaiting_value", False)

        user_inputs = await enrich_inputs_with_llm(user_inputs)

        if not await validate_and_continue(user_inputs): return True

        await cl.Message(content="✅ Inputs updated. Sending to backend...").send()
        try:
            r = await call_backend(user_inputs)
            if r.status_code == 200:
                await cl.Message(content="📈 Updated Recommendation:").send()
                await cl.Message(content=r.json()["advice"]).send()
                await cl.Message(content="Enter \n 'Modify' -> To change inputs \n \
                                                   'Done' -> To start over \n \
                                                   'Show User inputs' -> To display user inputs").send()
            else:
                await cl.Message(content=f"❌ Backend error: {r.status_code}").send()
        except (httpx.RequestError, Exception) as e:
            await cl.Message(content=f"❌ Backend is unreachable or failed: {e}. Restarting session...").send()
            await start()
        return True
    return True
