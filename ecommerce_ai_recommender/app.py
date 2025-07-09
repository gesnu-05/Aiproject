from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import pandas as pd
import os

app = FastAPI()

# Static files (CSS/JS if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML Templates
templates = Jinja2Templates(directory="templates")

# Ollama Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "granite3.2"  # Using Granite 3.2 for product recommendations

# Sample Product Database
products = [
    {"id": 1, "category": "Electronics", "name": "Wireless Earbuds"},
    {"id": 2, "category": "Electronics", "name": "Smartphone"},
    {"id": 3, "category": "Electronics", "name": "Laptop"},
    {"id": 4, "category": "Fashion", "name": "Leather Jacket"},
    {"id": 5, "category": "Fashion", "name": "Running Shoes"},
    {"id": 6, "category": "Home", "name": "Smart Vacuum Cleaner"},
    {"id": 7, "category": "Home", "name": "Air Purifier"},
]

df = pd.DataFrame(products)

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render index.html from the templates folder"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommend")
async def recommend_products(preferences: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    prompt = f"""You are an AI product recommender. Based on the user's preferences, suggest the best matching products from the following list:

Available Products:
{df.to_string(index=False)}

User Preferences: {preferences}

Recommended Products:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            headers=headers
        )

        print("Ollama Response:", response.text)

        try:
            json_response = json.loads(response.text.strip())
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from Ollama: {response.text.strip()}")

        recommendations = json_response.get("response", "No recommendations found.")
        return {"recommendations": recommendations}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
