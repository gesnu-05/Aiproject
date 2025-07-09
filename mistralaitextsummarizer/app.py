from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import ollama  # Assumes you're using ollama to run Mistral

app = FastAPI()

# Serve static files if needed in the future
# app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML frontend
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/summarize")
async def summarize(text: str = Form(...)):
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input is empty.")

        # Mistral via Ollama
        response = ollama.chat(
            model="mistral",
            messages=[
                {"role": "user", "content": f"Summarize the following:\n{text}"}
            ]
        )
        summary = response["message"]["content"]

        return {"summary": summary}

    except Exception as e:
        print("Error during summarization:", e)
        raise HTTPException(status_code=500, detail="Summarization failed.")
