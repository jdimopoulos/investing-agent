import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types
import traceback
import time

app = Flask(__name__)
# Enable CORS to allow the frontend on index.html to communicate with this server
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def extract_clean_json(text):
    """
    Safely extracts the raw JSON string from the model's output,
    removing any markdown code block wrappers (```json ... ```) dynamically.
    """
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def build_safe_response(ticker, sentiment="neutral", catalysts=None, risks=None, earnings_date="N/A", price_target="N/A", options_note="No data found.", thesis_check="—", company_name=""):
    """
    Builds a highly defensive dictionary matching index.html contracts exactly,
    now optimized for custom quant metrics.
    """
    if catalysts is None:
        catalysts = ["No data compiled."]
    if risks is None:
        risks = ["No data compiled."]
        
    return {
        "ticker": ticker,
        "company_name": company_name if company_name else f"{ticker} Inc.",
        "sentiment": sentiment,
        "sentiment_reason": f"Analysis executed for {ticker} using real-time search metrics.",
        "price_target": price_target,
        "earnings_date": earnings_date,
        "catalysts": catalysts,
        "risks": risks,
        "options_note": options_note,
        "thesis_check": thesis_check
    }

def analyze_single_ticker(ticker):
    """
    Performs search grounding and structures the payload for an individual ticker.
    Fuses the original qualitative data with the new option Greeks and valuation metrics.
    """
    prompt = (
        f"You are an expert institutional derivatives and equity research analyst. "
        f"Search the live web for the stock ticker: {ticker}. You must locate and extract specific quantitative metrics.\n\n"
        f"CRITICAL DATA TO LOCATE VIA SEARCH:\n"
        f"1. Forward P/E (Forward Price-to-Earnings Ratio)\n"
        f"2. Implied Volatility (IV) context, including current IV percentile or rank if available\n"
        f"3. General front-month option chain dynamics, focusing on roughly 30-50 delta strikes and typical Theta decay constraints.\n\n"
        f"Return your analysis as a raw, valid JSON object matching this schema exactly (do not output an array):\n\n"
        f"{{\n"
        f'  "ticker": "{ticker}",\n'
        f'  "company_name": "Full official company name",\n'
        f'  "sentiment": "Bullish, Neutral, or Bearish",\n'
        f'  "price_target": "Summarize recent price targets explicitly. Include Forward P/E ratio explicitly.",\n'
        f'  "earnings_date": "Month DD, YYYY (if found, else \'Not found\')",\n'
        f'  "catalysts": ["Catalyst 1", "Catalyst 2", "Catalyst 3"],\n'
        f'  "risks": ["Risk 1", "Risk 2"],\n'
        f'  "options_note": "State current IV percentile/rank. Summarize option chain: 30-50 Delta behaviors, major open interest strikes, or approx Theta decay impact.",\n'
        f'  "thesis_check": "Synthesize a 2-3 sentence technical thesis. Highlight how structural strategies (Delta Rolling, LEAPs, or spreads) fit current Forward P/E valuation and IV metrics."\n'
        f"}}\n\n"
        f"CRITICAL: Keep the response as a single raw JSON object. Do not wrap in markdown or backticks."
    )

    try:
    # Call Gemini 2.5 Flash with search tools enabled
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.15
            )
        )
    except Exception:
        time.sleep(3)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.15
            )
        )
        
        # Clean and parse the JSON response
        clean_json_str = extract_clean_json(response.text)
        parsed_data = json.loads(clean_json_str)
        
        # Ensure 'catalysts' and 'risks' are lists to protect frontend loops
        for key in ['catalysts', 'risks']:
            if key not in parsed_data:
                parsed_data[key] = ["No data compiled."]
            elif isinstance(parsed_data[key], str):
                parsed_data[key] = [parsed_data[key]]
                
        # Return a cleanly formatted response dictionary matching the build_safe_response schema
        return build_safe_response(
            ticker=ticker,
            company_name=parsed_data.get("company_name", f"{ticker} Inc."),
            sentiment=parsed_data.get("sentiment", "Neutral"),
            price_target=parsed_data.get("price_target", "N/A"),
            earnings_date=parsed_data.get("earnings_date", "Not found"),
            catalysts=parsed_data.get("catalysts"),
            risks=parsed_data.get("risks"),
            options_note=parsed_data.get("options_note", "No specialized option chain data resolved."),
            thesis_check=parsed_data.get("thesis_check", "No structural trade parameters evaluated.")
        )

    except Exception as e:
        print(f"Error handling ticker {ticker}: {str(e)}")
        print(traceback.format_exc())
        # Return a graceful, isolated fallback brief for this specific ticker
        return build_safe_response(
            ticker=ticker,
            options_note="Error compiling options chain metrics dynamically.",
            thesis_check="Check backend engine connection or API grounding thresholds."
        )

@app.route('/analyze', methods=['POST'])
def analyze_ticker():
    data = request.json or {}
    
    tickers_raw = data.get('tickers', data.get('ticker', '')).strip()
    
    # Split tickers by spaces or commas
    tickers = [t.strip().upper() for t in tickers_raw.replace(",", " ").split() if t.strip()]
    
    if not tickers:
        error_payload = build_safe_response(ticker="ERROR", options_note="No stock ticker was provided.")
        return jsonify({"briefs": [error_payload]}), 200

    # Limit to 6 tickers at a time
    if len(tickers) > 6:
        return jsonify({"error": "Please enter 6 or fewer tickers at a time"}), 400

    print(f"Backend: Analyzing tickers: {tickers}")
    
    briefs = []
    for ticker in tickers:
    brief = analyze_single_ticker(ticker)
    briefs.append(brief)
    time.sleep(5)  # 1 second pause between calls
                
    # Wrap results in the expected 'briefs' key
    return jsonify({"briefs": briefs}), 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    Stateless multi-turn conversation endpoint grounded with real-time Google Search.
    """
    data = request.json or {}
    message = data.get('message', '').strip()
    ticker = data.get('ticker', '').strip()
    history = data.get('history', [])
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
        
    print(f"Backend Chat: Processing prompt for context stock: {ticker if ticker else 'None'}")
    
    context_str = f"The user is currently examining the stock ticker: {ticker}. Prioritize specific options context, Forward P/E multiples, and recent catalysts for {ticker} if applicable to the query." if ticker else "The user is asking a general stock or derivatives market question."
    
    system_instruction = (
        "You are an expert institutional derivatives and equity research analyst assisting a professional trader using the Argos Pre-Trade Intelligence platform.\n"
        f"{context_str}\n"
        "Your task is to provide objective, quantitative, data-driven answers to the user's questions.\n"
        "Crucial: Always utilize your Google Search tool to search the live web for the absolute latest options chains, breaking headlines, structural metrics (IV percentile, Delta, Theta, P/E ratio), or historical contexts to back up your explanations.\n"
        "Answer concisely with professional markdown tables, key bullets, or clean short paragraphs. Be precise and avoid generic advice."
    )

    try:
        contents = []
        for turn in history:
            role = turn.get('role')
            if role == 'assistant':
                role = 'model'
            elif role != 'user' and role != 'model':
                role = 'user'
                
            contents.append({
                "role": role,
                "parts": [{"text": turn.get('content', '')}]
            })
            
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction=system_instruction,
                temperature=0.15
            )
        )
        
        return jsonify({"reply": response.text}), 200
        
    except Exception as e:
        print(f"Server Chat Error: {str(e)}")
        return jsonify({"error": f"Failed to compile response: {str(e)}"}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)