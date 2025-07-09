from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import os

app = FastAPI()

# Serve static files (if you plan to use CSS or JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set templates directory
templates = Jinja2Templates(directory="templates")

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama"

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render index.html from templates"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_code")
async def generate_code(prompt: str = Form(...), mode: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    if mode == "generate":
        full_prompt = f"Write a clean, well-documented {prompt} code snippet."
    elif mode == "debug":
        full_prompt = f"Debug and fix the following code:\n{prompt}"
    else:
        raise HTTPException(status_code=400, detail="Invalid mode selected.")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": full_prompt, "stream": False},
            headers=headers
        )

        print("Ollama Response:", response.text)

        try:
            json_response = json.loads(response.text.strip())
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama.")

        return {"code": json_response.get("response", "No valid response received.")}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# To run with `python app.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
