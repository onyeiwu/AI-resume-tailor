import os
import json
from groq import Groq
from groq import APIStatusError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "openai/gpt-oss-120b",
    "groq/compound-mini",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b"
]

CV_ANALYSIS_PROMPT = """You are a precise resume-parsing engine. You only output valid JSON.
Never include explanations, greetings, or markdown formatting like ```json blocks.

Extract the following from the resume text and return this exact JSON structure:

{
  "skills": ["list", "of", "skills", "mentioned"],
  "experience": [
    {"title": "job title", "company": "company name", "duration": "e.g. 2022-2024"}
  ],
  "education": [
    {"degree": "degree name", "institution": "school name", "year": "year or empty string"}
  ],
  "certifications": ["list", "of", "certifications"],
  "total_years_experience": 4,
  "highest_education_level": "one of: none, bachelor, master, phd, unspecified",
  "key_duties": ["short phrases describing what the candidate actually did in their roles"]
}

If a section is not present in the resume, return an empty list for it.
Do not invent information that is not in the text.

"total_years_experience" must be a single integer representing the candidate's total years of
relevant work experience, ONLY if this is clearly stated or reliably calculable from explicit dates
in the resume (e.g. "2020-2024" clearly gives 4 years). If job entries have no dates or duration
information, and no total is explicitly stated anywhere, return null. Do NOT guess or estimate
based on job titles or number of listed positions alone.

"highest_education_level" must be exactly one of: "none", "bachelor", "master", "phd", "unspecified",
based on the candidate's education section. Use "unspecified" only if no education section exists at all.

"key_duties" should be 1-6 word action phrases summarizing actual responsibilities from the
experience section (e.g. "prepared lesson plans", "managed client accounts"). Do not invent
duties not evidenced in the text.
"""

def analyze_cv(cv_text: str) -> dict:
    """
    Sends resume text to the LLM and returns structured data.
    Tries each model in MODELS in order, falling back if one is
    unavailable, rate-limited, or errors out.
    
    Args:
        cv_text: cleaned resume text
    
    Returns:
        A dictionary with skills, experience, education, certifications
    
    Raises:
        RuntimeError: if every model in the fallback chain fails
    """
    last_error = None
    
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": CV_ANALYSIS_PROMPT},
                    {"role": "user", "content": cv_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            raw_output = response.choices[0].message.content
            parsed = json.loads(raw_output)
            
            print(f"✓ Success using model: {model_name}")
            return parsed
        
        except APIStatusError as e:
            # This catches Groq-specific API errors: model not found,
            # rate limited, service unavailable, etc.
            print(f"✗ {model_name} failed ({e.status_code}), trying next model...")
            last_error = e
            continue
        
        except json.JSONDecodeError as e:
            # The model responded but didn't give valid JSON.
            # This is NOT an availability issue — retrying with another
            # model is still worth trying, since different models handle
            # JSON mode differently, but we log it distinctly so we can
            # tell the two failure types apart.
            print(f"✗ {model_name} returned invalid JSON, trying next model...")
            last_error = e
            continue
    
    # If we've gone through every model and none worked, fail loudly
    raise RuntimeError(f"All models failed. Last error: {last_error}")