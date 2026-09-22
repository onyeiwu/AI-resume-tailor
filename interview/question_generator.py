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

INTERVIEW_PROMPT = """You are an experienced technical interviewer preparing a candidate
for a job interview. Generate interview questions across four categories, based on the
real job description and the candidate's real resume data provided.

You only output valid JSON. Never include explanations outside the JSON structure.

Return this exact JSON structure:
{
  "technical_questions": [
    {"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "the exact text of the correct option"}
  ],
  "behavioral_questions": ["question 1", "question 2", ...],
  "role_specific_questions": [
    {"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "the exact text of the correct option"}
  ],
  "cv_based_questions": ["question 1", "question 2", ...]
}

RULES:
- technical_questions and role_specific_questions: multiple choice, exactly 4 options each,
  with one clearly correct answer and three plausible-but-wrong distractors. The
  "correct_answer" value must exactly match one of the 4 strings in "options".
- behavioral_questions and cv_based_questions: plain open-ended questions as strings — NO
  options, NO single correct answer, since these ask about the candidate's own real
  experience and have no objectively correct response.
- technical_questions: based on the job's required skills — general technical knowledge
  questions someone with those skills should be able to answer. Do not assume the candidate
  has skills not listed in their own data.
- role_specific_questions: multiple choice, based on best practices for the job's actual
  responsibilities.
- behavioral_questions: general professional behavioral questions relevant to the role
  (teamwork, conflict, prioritization, etc.).
- cv_based_questions: ONLY reference real items from the candidate's actual experience,
  duties, or skills provided below — do not invent any employer, project, number, or detail
  not present in the data. If referencing a specific duty, do not attach it to a specific
  employer unless the data explicitly links them. Ask the candidate to elaborate on real
  things they've listed, and never state a specific number or percentage that is not
  explicitly present in the original data.
- Produce 5-6 questions per category.
"""
def generate_interview_questions(cv_analysis: dict, jd_analysis: dict) -> dict:
    """
    Generates technical, behavioral, role-specific, and CV-based interview
    questions grounded in the real CV and JD data.
    
    Args:
        cv_analysis: the full result dict from analyze_cv()
        jd_analysis: the full result dict from analyze_jd()
    
    Returns:
        A dict with four lists of questions, one per category
    """
    context = f"""
JOB DATA:
Job title: {jd_analysis.get('job_title', '')}
Required skills: {jd_analysis.get('required_skills', [])}
Key responsibilities: {jd_analysis.get('key_responsibilities', [])}

CANDIDATE'S REAL DATA:
Skills: {cv_analysis.get('skills', [])}
Experience: {cv_analysis.get('experience', [])}
Key duties: {cv_analysis.get('key_duties', [])}
"""
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": INTERVIEW_PROMPT},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            return json.loads(response.choices[0].message.content)
        except (APIStatusError, json.JSONDecodeError) as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")