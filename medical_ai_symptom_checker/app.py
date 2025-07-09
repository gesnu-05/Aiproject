from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import os

app = FastAPI()

# Serve static assets (if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Ollama & MedLLaMA 2 settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "medllama2"

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render the symptom checker UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze_symptoms")
async def analyze_symptoms(symptoms: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    prompt = f"""You are a medical AI assistant trained to analyze symptoms. 
Based on the provided symptoms, give possible explanations and general advice. 
Do not provide a diagnosis or replace a doctor's consultation.

User Symptoms: {symptoms}

Medical AI:"""

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

        ai_response = json_response.get("response", "I'm sorry, but I couldn't generate a response.")
        return {"response": ai_response}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run server via: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
