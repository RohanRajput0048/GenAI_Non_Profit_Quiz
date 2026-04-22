from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os

from backend.models import QuizGenerationRequest, EvaluationRequest
from backend.llm_service import generate_quiz_content, evaluate_response

load_dotenv()

app = FastAPI(title="Non-Profit Educational Bot API", version="1.0.0")

@app.post("/generate_quiz")
async def generate_quiz(request: QuizGenerationRequest):
    try:
        quiz_response = generate_quiz_content(request.email_text)
        return {"content": quiz_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate_answer")
async def evaluate_answer(request: EvaluationRequest):
    try:
        evaluation = evaluate_response(request.user_input, request.chat_history)
        return {"content": evaluation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
