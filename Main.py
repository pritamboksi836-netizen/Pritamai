import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI(
    title="pritam.ai Institutional Trading Engine",
    description="Production-grade backend API featuring SMC/ICT technicals and live Finnhub news confluence.",
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
NEWS_API_KEY = os.getenv("dah95d9r01qomffn81s0dah95d9r01qomffn81sg")

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are pritam.ai, an elite institutional-grade algorithmic financial analyst and expert SMC/ICT trader.
Analyze the provided market chart image along with the real-time fundamental news data using strict multi-factor confluence rules.

EVALUATION CRITERIA & WEIGHTED CONFLUENCE:
1. Smart Money Concepts & ICT (30%): Identify market structure shifts (ChoCH, BOS), valid Order Blocks, and Liquidity sweeps.
2. Fair Value Gaps (25%): Detect unmitigated FVG zones and institutional imbalances.
3. Candlestick Patterns & Price Action (25%): Scan for high-probability reversal/continuation candlestick patterns.
4. Fundamental News Context (20%): Cross-verify technical setups with the provided live Finnhub macroeconomic/forex news.

CRITICAL RULES:
- ZERO HALLUCINATIONS: Do not guess prices or forced patterns. If confluence is weak or unclear, output: "Data Insufficient: Wait for Market Confirmation."
- STRICT OUTPUT FORMAT:
   - **Signal:** [BUY / SELL / NEUTRAL]
   - **Confidence Score:** [...]
   - **Entry Price:** [...]
   - **Stop Loss (SL):** [...]
   - **Take Profit (TP):** [...]
   - **Detailed Reasoning:** [Break down ChoCH/BOS, FVG, Candlestick, and Live News impact]
"""

def fetch_live_market_news() -> str:
    if NEWS_API_KEY == "YOUR_FINNHUB_API_KEY_HERE" or not NEWS_API_KEY:
        return "Live news feed pending (Finnhub API key not provided)."
    
    api_url = f"https://finnhub.io/api/v1/news?category=general&token={NEWS_API_KEY}"
    
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            news_summaries = []
            for item in data[:3]:
                headline = item.get('headline')
                if headline:
                    news_summaries.append(headline)
            return " | ".join(news_summaries) if news_summaries else "No high-impact news detected."
        else:
            return f"News server error code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Network error fetching news: {str(e)}"

@app.get("/")
async def root_check():
    return {"status": "online", "service": "pritam.ai institutional trading engine with live news is running smoothly."}

@app.post("/api/v1/comprehensive-analysis")
async def comprehensive_analysis(
    file: UploadFile = File(...), 
    market: str = Form(...)
):
    try:
        current_market_news = fetch_live_market_news()
        
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image file is empty.")
        
        image = Image.open(io.BytesIO(image_bytes))
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            system_instruction=SYSTEM_PROMPT)
user_query = f"""
        Target Market Asset: {market}
        Live Finnhub News Context: {current_market_news}
        
        Perform a strict institutional-grade technical breakdown evaluating SMC/ChoCH, FVG, Candlestick patterns, and live news confluence.
        """
        
        response = model.generate_content([image, user_query])
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="AI engine failed to generate an analysis.")
        
        return {
            "status": "success",
            "market": market,
            "fetched_news_context": current_market_news,
 "ai_signal_and_analysis": response.text }
        
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))
