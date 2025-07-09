from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import os

app = FastAPI()

# Static files (optional CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# API Configuration
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
NEWS_API_KEY = "YOUR_REAL_API_KEY"  # Replace with your actual API key
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5"  # Using Qwen2.5 for summarization

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render the main page from templates/index.html"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/fetch_news")
def fetch_and_summarize_news(category: str = Query("technology")):
    """Fetch latest news articles and summarize using Ollama"""
    params = {
        "category": category,
        "language": "en",
        "apiKey": NEWS_API_KEY
    }

    try:
        news_response = requests.get(NEWS_API_URL, params=params)

        if news_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch news articles")

        news_data = news_response.json()
        if not news_data.get("articles"):
            return {"summary": "No news articles found for this category."}

        # Extract titles of top 3 articles
        articles = news_data["articles"][:3]
        headlines = "\n".join([f"- {a['title']} ({a['source']['name']})" for a in articles])

        # Summarize using Ollama
        prompt = f"Summarize these news headlines:\n{headlines}"
        ollama_response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        )

        print("Ollama Response:", ollama_response.text)

        try:
            summary_data = json.loads(ollama_response.text.strip())
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON from Ollama")

        summary = summary_data.get("response", "No summary available.")
        return {"summary": summary, "articles": articles}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)








