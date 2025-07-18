
from langchain_google_genai import ChatGoogleGenerativeAI
from env import import_my_env
from data_cache import forecast_data

import_my_env()
#GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

def build_structured_prompt(user_input, stock_summaries: dict):
    prompt = "[INST]<<SYS>>"
    prompt += (
        "You are a financial advisor. Your task is to recommend 5–10 stocks based on recent news, basic financial data, and the user's preferences."
        "For each selected stock, provide ONLY: (1) one-line summary (e.g. good growth, or strong sentiment), (2) one-line concern (e.g. high P/E, or weak margins), and (3) Expected growth percentage (4) percentage to invest.(e.g Invest: 10%)"
        "Keep each stock's section brief (max 2 lines + %)."
        "End with a final summary table showing percentage allocation."
        "\nHere is an example format you must follow exactly:\n"
        "1. SOLARA\n"
           "Summary: High growth potential with strong margin improvement.\n"
           "Concern: Extremely high P/E ratio.\n"
           "Growth: 21.46%\n"
           "Invest: 15%\n"
        "2. INDOCO\n"
           "Summary: Leading growth stock with strong insider confidence.\n"
           "Concern: P/E ratio is not available.\n"
           "Growth: 16.97%\n"
           "Invest: 15%\n"
        "3. LAURUSLABS\n"
           "Summary: High insider ownership suggests confidence.\n"
           "Concern: High P/E ratio.\n"
           "Growth: 15.64%\n"
           "Invest: 15%\n"
        "Summary Table:\n"
        "| Stock        | Allocation |\n"
        "|--------------|------------|\n"
        "| SOLARA       | 15%        |\n"
        "| INDOCO       | 15%        |\n"
        "| LAURUSLABS   | 15%        |\n"
        "\n<</SYS>>\n"
    )

    for symbol, summary in stock_summaries.items():
        growth_pct = forecast_data.get(symbol, 0.0) * 100
        prompt += f"[{symbol} Intro]: {summary['intro'][:200]}\n"
        prompt += f"[{symbol} Growth]: Forecasted Growth ~ {growth_pct:.2f}%\n"
        prompt += f"{summary['movement']}\n"

        prompt += "News:\n"
        for h in summary.get("headlines", [])[:1]:
            prompt += f"- {h}\n"

        prompt += "Financials:\n"
        for line in summary.get("financials", [])[:2]:
            prompt += f"- {line}\n"

    prompt += "Please recommend the top stocks. Keep your answers concise and actionable."
    prompt += "[/INST]"
    return prompt

#def get_final_stock_advice(user_input: dict, stock_summaries: dict) -> str:
def get_final_stock_advice(user_input: dict, stock_summaries: dict) -> tuple[str, dict]:

    print("########get_final_stock_advice")
    print("#### stock_summaries ####\n", stock_summaries)
    prompt = build_structured_prompt(user_input, stock_summaries)
    print("\n###### Prompt - Start#####\n")
    print(prompt)
    print("\n###### Prompt - End  #####\n")
    result = llm.invoke(prompt)
    #return result.content
    return result.content, stock_summaries

