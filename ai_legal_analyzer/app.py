from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json

app = FastAPI()

# Serve static assets (CSS, JS, etc. if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use templates directory
templates = Jinja2Templates(directory="templates")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi"  # Using Phi for legal document analysis

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render the index.html from templates"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze_legal_text")
async def analyze_legal_text(text: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    prompt = f"""Extract key insights from the following legal document:
{text}

Summarize important clauses, risks, and obligations."""

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

        insights = json_response.get("response", "No insights generated.")
        return {"insights": insights}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
