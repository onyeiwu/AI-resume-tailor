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

EXPERIENCE_TAILOR_PROMPT = """You are a professional resume editor. You rewrite a candidate's
work accomplishments into polished, achievement-oriented resume bullet points, emphasizing
relevance to a specific job — WITHOUT inventing any new facts, tools, techniques, numbers,
or outcomes not already present in the candidate's real data provided to you.

You only output valid JSON. Never include explanations outside the JSON structure.

STRICT RULES:
- You may rephrase, reorder, combine, and re-emphasize the candidate's real duties.
- You may NOT introduce any tool, technique, metric, or outcome not already present in the
  data provided — e.g. do not add specific techniques, numbers, or percentages that were not stated.
- Do NOT claim a specific categorization (like "RESTful") unless it is explicitly stated in
  the original data.
- Produce between 4 and 8 bullet points, each starting with a strong action verb.

Return this exact JSON structure:
{
  "bullets": ["bullet point 1", "bullet point 2", ...]
}
"""

def tailor_experience(cv_analysis: dict, jd_analysis: dict) -> list:
    """
    Rewrites the candidate's real key duties into polished, JD-relevant
    resume bullet points, using only real content.
    
    Args:
        cv_analysis: the full result dict from analyze_cv()
        jd_analysis: the full result dict from analyze_jd()
    
    Returns:
        A list of bullet point strings
    """
    context = f"""
Candidate's real duties/accomplishments: {cv_analysis.get('key_duties', [])}
Candidate's real skills: {cv_analysis.get('skills', [])}

Job title: {jd_analysis.get('job_title', '')}
Job's key responsibilities: {jd_analysis.get('key_responsibilities', [])}
Job's required skills: {jd_analysis.get('required_skills', [])}
"""
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": EXPERIENCE_TAILOR_PROMPT},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get('bullets', [])
        except (APIStatusError, json.JSONDecodeError) as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")