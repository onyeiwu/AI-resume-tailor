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

SUMMARY_TAILOR_PROMPT = """You are a professional resume editor. You rewrite a candidate's
professional summary to better emphasize relevance to a specific job — WITHOUT inventing
any new facts, skills, tools, employers, or experience that are not already present in the
original resume content provided.

STRICT RULES:
- You may rephrase, reorder, and re-emphasize existing content.
- You may NOT introduce any skill, tool, technology, employer, achievement, or qualification
  that does not already appear somewhere in the candidate's resume data provided to you.
- If the job wants something the candidate doesn't have, simply do not mention it — do not
  imply the candidate has it.
- Keep the tone professional and concise, 3-5 sentences.

Return ONLY the rewritten summary text. No explanations, no markdown, no extra commentary.
"""

def tailor_summary(cv_analysis: dict, jd_analysis: dict) -> str:
    """
    Rewrites a professional summary using only real content from the CV,
    emphasized toward relevance for the given job.
    
    Args:
        cv_analysis: the full result dict from analyze_cv()
        jd_analysis: the full result dict from analyze_jd()
    
    Returns:
        The rewritten summary as plain text
    """
    # We pass the CV's REAL extracted data as grounding context —
    # the model can only draw from what's actually here
    context = f"""
Candidate's real skills: {cv_analysis.get('skills', [])}
Candidate's real experience: {cv_analysis.get('experience', [])}
Candidate's real education: {cv_analysis.get('education', [])}
Candidate's real key duties: {cv_analysis.get('key_duties', [])}

Job title: {jd_analysis.get('job_title', '')}
Job's key requirements: {jd_analysis.get('required_skills', [])}
"""
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SUMMARY_TAILOR_PROMPT},
                    {"role": "user", "content": context}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except APIStatusError as e:
            print(f"✗ {model_name} failed ({e.status_code}), trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")