import os
import json
from groq import Groq
from groq import APIStatusError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "qwen/qwen3.6-27b"
]

FEEDBACK_PROMPT = """You are a supportive but honest interview coach. You are given an
interview question and the candidate's own typed answer. Give brief, constructive
feedback on how they could strengthen their answer — structure, specificity, confidence —
based ONLY on what they actually wrote. Do not invent details about their experience;
only comment on how they communicated what they already said.

You only output valid JSON. Never include explanations outside the JSON structure.

Return this exact structure:
{
  "feedback": "2-3 sentences of constructive, encouraging feedback on how to strengthen this answer"
}

If the candidate left the answer blank or very short, gently note that a fuller answer
with a specific example would make it stronger.
"""

def review_answer(question: str, user_answer: str) -> str:
    """
    Gives brief coaching feedback on a candidate's own typed interview answer.
    Does not grade or judge correctness — there is no single right answer for
    open-ended questions. Only comments on how the answer was communicated.
    """
    context = f"Question: {question}\n\nCandidate's answer: {user_answer}"
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": FEEDBACK_PROMPT},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            result = json.loads(response.choices[0].message.content)
            return result.get('feedback', '')
        except (APIStatusError, json.JSONDecodeError) as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")