import os
import json
from groq import Groq
from groq import APIStatusError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "groq/compound-mini",
    "qwen/qwen3.6-27b"
]

SKILLS_TAILOR_PROMPT = """You are a resume editor. You are given a candidate's EXACT list
of real skills and a job's required skills. Your job is to REORDER the candidate's real
skills list so the most relevant ones for this job appear first.

You only output valid JSON. Never include explanations outside the JSON structure.

STRICT RULES:
- You may ONLY reorder the exact skills given to you.
- You may NOT add, rename, merge, split, or rephrase any skill.
- Every skill in the input list must appear exactly once in your output, with identical spelling.
- Do not remove any skill, even if it seems irrelevant to the job — just place it later in the list.

Return this exact JSON structure:
{
  "reordered_skills": ["skill1", "skill2", ...]
}
"""

def tailor_skills(cv_skills: list, jd_required_skills: list) -> list:
    """
    Reorders a candidate's real skills to emphasize relevance to a job.
    Never adds, removes, or rephrases any skill.
    
    Args:
        cv_skills: the candidate's real skills list from analyze_cv()
        jd_required_skills: the job's required_skills from analyze_jd()
    
    Returns:
        The same skills, reordered by relevance
    """
    context = f"""
Candidate's exact real skills list: {cv_skills}
Job's required skills: {jd_required_skills}
"""
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SKILLS_TAILOR_PROMPT},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content)
            return result.get('reordered_skills', [])
        except (APIStatusError, json.JSONDecodeError) as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")