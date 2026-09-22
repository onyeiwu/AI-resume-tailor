import os
from groq import Groq
from groq import APIStatusError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-20b",
    "groq/compound-mini"
    
]

def build_system_prompt(cv_analysis: dict = None, jd_analysis: dict = None) -> str:
    """
    Builds the chat's system prompt, including the user's real CV/JD
    data if it's available, so the AI can ground its answers in real
    information rather than generic advice.
    """
    base = """You are a friendly, knowledgeable career coach and assistant. You help
people think through their skills, career direction, and job search strategy.

STRICT RULES:
- If the person's real CV or job description data is provided below, you may
  reference it, but you must NEVER invent or assume details about their
  experience that aren't explicitly stated in that data.
- If no CV/JD data is provided, have a normal, helpful career conversation
  based only on what the person tells you directly in the chat.
- Be conversational, warm, and direct — like a good mentor, not a generic
  chatbot. Ask clarifying questions when helpful.
- You do not have the ability to browse the internet or search for live job
  postings. If asked, be honest that this isn't something you can do yet.
"""
    if cv_analysis:
        base += f"\n\nThe user's REAL analyzed resume data:\n{cv_analysis}"
    if jd_analysis:
        base += f"\n\nThe user's REAL analyzed job description data:\n{jd_analysis}"
    return base

def get_chat_response(messages: list, cv_analysis: dict = None, jd_analysis: dict = None) -> str:
    """
    Sends the full conversation history to the LLM and gets back the
    next response, with model fallback.
    
    Args:
        messages: list of {"role": "user"/"assistant", "content": "..."} dicts,
                  the conversation so far
        cv_analysis, jd_analysis: optional real data for grounding
    
    Returns:
        The AI's reply text
    """
    system_prompt = build_system_prompt(cv_analysis, jd_analysis)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=full_messages,
                temperature=0.6
            )
            return response.choices[0].message.content
        except APIStatusError as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")