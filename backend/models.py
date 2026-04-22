from pydantic import BaseModel
from typing import List, Dict

class QuizGenerationRequest(BaseModel):
    email_text: str

class ChatMessage(BaseModel):
    role: str
    content: str

class EvaluationRequest(BaseModel):
    user_input: str
    chat_history: List[ChatMessage]
