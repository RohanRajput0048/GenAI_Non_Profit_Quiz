import os
from google import genai
from google.genai import types
from backend.database import get_relevant_context

def setup_client():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
    return client

def generate_quiz_content(email_text: str) -> str:
    if not os.getenv("GEMINI_API_KEY"):
         return "Please set your GEMINI_API_KEY in the `.env` file first!"
    try:
        client = setup_client()
        prompt = (
            "You are an expert training scenario generator for a non-profit organization.\n"
            "Generate exactly 5 Multiple Choice Questions (MCQs) based on the following donor email. "
            "Each question should test the trainee's understanding of donor intent and non-profit domain knowledge.\n"
            "You MUST output valid JSON format ONLY. The JSON must be an array of objects, where each object has "
            "a 'question' property (string) and an 'options' property (an array of exactly 4 strings: A, B, C, D). "
            "Do NOT provide the correct answer key in your output.\n\n"
            f"Donor Email:\n{email_text}"
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.text
    except Exception as e:
        return f"An error occurred while generating the quiz: {str(e)}"

def evaluate_response(user_input: str, chat_history: list) -> str:
    if not os.getenv("GEMINI_API_KEY"):
         return "Please set your GEMINI_API_KEY in the `.env` file first!"
    
    try:
        client = setup_client()
        context = get_relevant_context(user_input)
        
        system_instruction = (
            "You are an AI evaluator for a Non-Profit organization training program. "
            "Your job is to assess the user's proposed response to a hypothetical donor email, or their answers to a generated quiz. "
            "Use the provided context (internal rules) to determine if their response is correct, helpful, and safe. "
            "If they are answering a quiz, format your output EXACTLY like a scorecard:\n"
            "1. Give an overall Score (e.g., 4/5) at the very top using Markdown Header formatting (###).\n"
            "2. Go through EACH question individually. You MUST explicitly state if they were `:green[Correct]` or `:red[Incorrect]` using this exact text syntax.\n"
            "3. Crucially, provide the exact CORRECT options for each question, and explain WHY based on the internal rules.\n"
            "4. Give an overall summary of their performance at the end.\n"
            "Context rules retrieved from database:\n"
            f"{context}\n\n"
        )
        
        prompt = system_instruction
        for msg in chat_history[:-1]:
            role = "User" if msg.role == "user" else "Assistant"
            prompt += f"{role}: {msg.content}\n"
            
        prompt += f"User: {user_input}\nAssistant:"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"
