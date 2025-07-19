
import re
import json
import httpx
import chainlit as cl
from langchain_google_genai import ChatGoogleGenerativeAI
from app.env import import_my_env

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
    ("monthly_income", "What is your monthly income in INR?", float, lambda x: x >= 0),
    ("monthly_expenses", "What are your monthly expenses in INR?", float, lambda x: x >= 0),
    ("monthly_investment", "How much do you invest monthly in INR?", float, lambda x: x >= 0),
    ("annual_extra_investment", "Any annual extra investment (INR)?", float, lambda x: x >= 0),
    ("current_savings", "How much are your current savings (INR)?", float, lambda x: x >= 0),
    ("risk_percent", "What is your risk tolerance? (0–100%)", int, lambda x: 0 <= x <= 100),
    ("years", "What is your investment horizon in years?", int, lambda x: 1 <= x <= 20),
    ("expected_returns_percent", "What returns do you expect annually? (1–20%)", int, lambda x: 1 <= x <= 20),
    ("num_dependents", "How many dependents do you have? (0–10)", int, lambda x: 0 <= x <= 10),
    ("investment_type", "What is your investment style? (Aggressive, Moderate, Slow)", str, lambda x: x in ["Aggressive", "Moderate", "Slow"]),
    ("investor_knowledge", "What is your investor knowledge level? (Beginner, Intermediate, Expert)", str, lambda x: x in ["Beginner", "Intermediate", "Expert"]),
    ("interested_sectors", f"Which sectors are you interested in? Provide a comma-separated list from:{', '.join(sector_list)}", list, lambda x: isinstance(x, list)),
    ("has_health_insurance", "Do you have health insurance? (yes/no)", bool, lambda x: isinstance(x, bool)),
    ("has_emergency_fund", "Do you have an emergency fund? (yes/no)", bool, lambda x: isinstance(x, bool)),
]

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

        prompt = build_user_data_prompt(user_inputs)
        print(f"##### Prompt: {prompt}")
        response = llm.invoke(prompt)
        print(f"##### Response: {response}")
        raw_output = response.content.strip()
        clean_output = re.sub(r"^```json\n|```$", "", raw_output, flags=re.MULTILINE).strip()
        parsed = json.loads(clean_output)
        user_inputs.update(parsed)
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
        
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post("http://backend:8000/recommend", json=user_inputs)
            #r = await client.post("http://127.0.0.1:8010/recommend", json=user_inputs)
            
        print(f"##### Backend response:{r}")
        if r.status_code == 200:
            await cl.Message(content="📈 Recommendation Result:").send()
            await cl.Message(content=r.json()["advice"]).send()
            await cl.Message(content="If you like to modify inputs type 'Modify'. If you are done type 'Done'").send()
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

    if content.lower() == "modify":
        await cl.Message(content="Please provide the inputs you want to modify from:\n`interested_sectors`, `risk_percent`, `years`, `expected_returns_percent`, `investment_type`").send()
        cl.user_session.set("awaiting_modification_list", True)
        return

    if cl.user_session.get("awaiting_modification_list"):
        modifiable_keys = ["interested_sectors", "risk_percent", "years", "expected_returns_percent", "investment_type"]
        requested_keys = [k.strip().lower() for k in content.lower().split(",") if k.strip().lower() in modifiable_keys]
        if not requested_keys:
            await cl.Message(content="❌ Invalid fields. Please choose from: " + ", ".join(modifiable_keys)).send()
            return
        cl.user_session.set("modify", requested_keys)
        cl.user_session.set("modify_index", 0)
        cl.user_session.set("awaiting_value", False)
        cl.user_session.set("awaiting_modification_list", False)

    if cl.user_session.get("modify") is not None:
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
                        
                        # ✅ validate just the modified field
                        validation_errors = validate_user_inputs(user_inputs)
                        if validation_errors:
                            await cl.Message(content="❌ Validation error:\n" + "\n".join(validation_errors)).send()
                            await cl.Message(content=f"Let's update: {questions[current_index][1]}").send()
                            return
                    except:
                        await cl.Message(content="❌ Invalid input. Please try again.").send()
                        await cl.Message(content=question).send()
                        return

        if cl.user_session.get("modify_index", 0) < len(modify_keys):
            mod_key = modify_keys[cl.user_session.get("modify_index")]
            for key, question, *_ in questions:
                if key == mod_key:
                    cl.user_session.set("awaiting_value", True)
                    await cl.Message(content=f"🔁 Let's update: {question}").send()
                    return
        else:
            cl.user_session.set("modify", None)
            cl.user_session.set("modify_index", 0)
            cl.user_session.set("awaiting_value", False)
            prompt = build_user_data_prompt(user_inputs)
            print(f"##### Prompt: {prompt}")
            response = llm.invoke(prompt)
            print(f"##### Response: {response}")
            raw_output = response.content.strip()
            clean_output = re.sub(r"^```json\n|```$", "", raw_output, flags=re.MULTILINE).strip()
            try:
                parsed = json.loads(clean_output)
                user_inputs.update(parsed)
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
                await cl.Message(content="✅ Inputs updated. Sending to backend...").send()
                try:
                    async with httpx.AsyncClient(timeout=60) as client:
                        r = await client.post("http://backend:8000/recommend", json=user_inputs)
                        #r = await client.post("http://127.0.0.1:8010/recommend", json=user_inputs)
                        
                        
                    print(f"##### Backend response:{r}")
                    if r.status_code == 200:
                        await cl.Message(content="📈 Updated Recommendation:").send()
                        await cl.Message(content=r.json()["advice"]).send()
                        await cl.Message(content="Type `Modify` to change inputs or `Done` to start over.").send()
                    else:
                        await cl.Message(content=f"❌ Backend error: {r.status_code}").send()
                except (httpx.RequestError, Exception) as e:
                    await cl.Message(content=f"❌ Backend is unreachable or failed: {e}. Restarting session...").send()
                    await start()
            except Exception as e:
                await cl.Message(content=f"❌ Failed to parse JSON: {e}").send()
            return

    current_index = cl.user_session.get("current_index")
    if current_index >= len(questions):
        await cl.Message(content="✅ All inputs collected. Type 'Done' to restart or 'Modify' to change inputs.").send()
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
