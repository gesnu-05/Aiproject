from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import os

app = FastAPI()

# Serve static files (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use the templates directory for HTML files
templates = Jinja2Templates(directory="templates")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwq"  # Using QWQ for customer support chatbot

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render the homepage using templates/index.html"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_ai(user_query: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    # Construct prompt for customer support
    prompt = f"""You are a customer support chatbot. Answer the user's question professionally and concisely.
User: {user_query}
Chatbot:"""

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

        chatbot_response = json_response.get("response", "I'm sorry, but I couldn't generate a response.")
        return {"response": chatbot_response}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the FastAPI server directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
