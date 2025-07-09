from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import datetime

app = FastAPI()

# Static files (CSS, JS if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates (for rendering index.html)
templates = Jinja2Templates(directory="templates")

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama2"

# In-memory task storage
scheduled_tasks = []

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Render index.html from templates"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_ai(user_query: str = Form(...)):
    headers = {"Content-Type": "application/json"}

    # Build prompt for virtual assistant
    prompt = f"""You are an AI-powered virtual assistant that helps with task scheduling and answering queries.
If the user asks to schedule a task, extract the task details and save it.
User: {user_query}
Assistant:"""

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

        # Detect scheduling intent
        if "schedule" in user_query.lower() or "remind" in user_query.lower():
            task = {
                "task": user_query,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            scheduled_tasks.append(task)
            chatbot_response += f"\n📝 Task Scheduled: {user_query}"

        return {"response": chatbot_response, "tasks": scheduled_tasks}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the server with: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
