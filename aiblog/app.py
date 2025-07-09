from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import json

app = FastAPI()

# Mount static directory if needed in future
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_content(topic: str = Form(...), style: str = Form(...)):
    headers = {"Content-Type": "application/json"}
    prompt = f"Write a detailed blog post about '{topic}' in a {style} tone."

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error from Ollama API")

        try:
            json_response = response.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama")

        generated_content = json_response.get("response", "No content generated.")
        return {"content": generated_content}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

