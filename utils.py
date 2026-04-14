import os
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions

# Setup Database connection
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")

# Setup Gemini. Make sure to have GEMINI_API_KEY in your .env
def setup_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    return model

# Add sample data for the bot to retrieve (Mock data for now)
def initialize_knowledge_base():
    collection = chroma_client.get_or_create_collection(name="guidelines")
    if collection.count() == 0:
        collection.add(
            documents=[
                "Rule 1: Always greet donors with gratitude and refer to their past contributions.",
                "Rule 2: Do not promise specific outcomes for donations unless stated in the official campaign.",
                "Rule 3: Transparency is key. Always be ready to provide our annual financial report if asked.",
                "Rule 4: When an email is angry about a late tax receipt, apologize sincerely and promise action within 24 hours."
            ],
            metadatas=[{"source": "donor_policy"}, {"source": "donor_policy"}, {"source": "transparency"}, {"source": "complaint_policy"}],
            ids=["doc1", "doc2", "doc3", "doc4"]
        )
    return collection

def get_relevant_context(user_query):
    collection = initialize_knowledge_base()
    results = collection.query(
        query_texts=[user_query],
        n_results=2
    )
    if results['documents'] and len(results['documents']) > 0:
        return "\n".join(results['documents'][0])
    return "No specific context found."

def get_llm_response(user_input, chat_history):
    # Dummy mock string if you haven't set your API key yet
    if not os.getenv("GEMINI_API_KEY"):
         return "Please set your GEMINI_API_KEY in the `.env` file first!"
    
    try:
        model = setup_llm()
        
        # Retrieve relevant non-profit guidelines from Vector DB
        context = get_relevant_context(user_input)
        
        # Build prompt considering past chat history
        system_instruction = (
            "You are an AI evaluator for a Non-Profit organization training program. "
            "Your job is to assess the user's proposed response to a hypothetical donor email. "
            "Use the provided context (internal rules) to determine if their response is correct, helpful, and safe. "
            "Do not just say correct/incorrect; provide deep contextual explanations for incorrect answers to create a personalized learning loop. "
            "Context rules retrieved from database:\n"
            f"{context}\n\n"
        )
        
        prompt = system_instruction
        for msg in chat_history[:-1]:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
            
        prompt += f"User: {user_input}\nAssistant:"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"
