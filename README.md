# Argos — Pre-Trade Intelligence Agent

A browser-based investing research agent powered by the Anthropic Claude API with web search.

## Live Demo
https://investing-agent-7uiz.onrender.com

> Note: The app may take 30–60 seconds to load if it hasn't been 
> visited recently (free tier cold start).

## What It Does
- Enter up to 6 stock tickers and get a Buy / Hold / Sell rating for each
- Each rating includes a live web-searched pro and con list 
  plus an additional insights section
- Built-in chatbot for follow-up questions about any stock

## Tech Stack
- Python / Flask backend
- Google Gemini API with web search grounding
- Deployed on Render

## Setup (one time)

**1. Install Python dependencies**
```bash
pip install flask anthropic
```

**2. Set your Anthropic API key**

Get your key at: https://console.anthropic.com

Mac/Linux:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Windows (Command Prompt):
```
set ANTHROPIC_API_KEY=sk-ant-...
```

Windows (PowerShell):
```
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

## Run

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## Usage

- Enter up to 6 ticker symbols (e.g. `NVDA, AMD, TSLA`)
- Hit Enter or click "Run Analysis"
- Wait 15–30 seconds while Claude searches the web
- Get structured pre-trade briefs covering:
  - Sentiment (Bullish / Neutral / Bearish)
  - Analyst price targets
  - Upcoming earnings date
  - Key catalysts and risks
  - Options-relevant context
  - Thesis check paragraph

## Cost

Each run uses Claude Sonnet with web search. Typical cost: ~$0.05–0.15 per run depending on tickers.
Check usage at: https://console.anthropic.com/usage
