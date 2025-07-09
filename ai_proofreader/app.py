from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json

app = FastAPI()

# Serve static assets if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set templates directory
templates = Jinja2Templates(directory="templates")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1"  # Using DeepSeek R1 for grammar & spell checking

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render index.html from templates"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/proofread")
async def proofread_text(text: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    prompt = f"Correct the grammar, spelling, and sentence structure of the following text:\n{text}"

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
            raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama.")

        corrected = json_response.get("response", "No valid response received.")
        return {"corrected_text": corrected}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the server with: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
