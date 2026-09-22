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

JD_ANALYSIS_PROMPT = """You are a precise job-description parsing engine. You only output valid JSON.
Never include explanations, greetings, or markdown formatting like ```json blocks.

Extract the following from the job description text and return this exact JSON structure:

{
  "job_title": "the job title",
  "required_skills": ["short skill phrases only, 1-4 words each"],
  "preferred_skills": ["short skill phrases only, 1-4 words each"],
  "responsibilities": ["list", "of", "key", "responsibilities"],
  "qualifications": ["degree requirements, certifications, years of experience — full statements belong here, NOT in skills"],
  "keywords": ["important", "recurring", "terms", "or", "phrases", "for", "ATS", "matching"],
  "years_required": 5
  "education_required": "one of: none, bachelor, master, phd, unspecified"
  "key_responsibilities": ["short 2-5 word phrases summarizing the core responsibilities, same style as: 'develop backend APIs', 'manage cloud infrastructure'"]
}

STRICT RULES:
- required_skills and preferred_skills must be SHORT PHRASES (1-4 words), like "SAP", "budgeting", "project accounting" — never full sentences.
- Anything about degrees, certifications, or years of experience belongs ONLY in "qualifications", never in the skills lists.
- Example of CORRECT skill formatting: "financial reporting", "SAP", "Microsoft Excel"
- Example of WRONG skill formatting (do not do this): "Advanced proficiency in Microsoft Excel, including financial analysis, reporting, and modelling"
- "years_required" must be a single integer — the MINIMUM years mentioned. If the text says "7-10 years", use 7. If the text says "3+ years", use 3. If no years requirement is mentioned anywhere, use null.
- "education_required" must be exactly one of: "none", "bachelor", "master", "phd", "unspecified". Use "unspecified" if no degree requirement is mentioned. Use "none" only if the posting explicitly states no degree is required.
- "key_responsibilities" must be SHORT PHRASES (2-5 words each), extracting the core action from each responsibility — NOT full sentences. This is separate from the full-sentence "responsibilities" list above; key_responsibilities exists specifically for phrase-level comparison against a candidate's CV.
- Example: "Develop and integrate RESTful APIs and third-party services" becomes "integrate RESTful APIs"

If a section is not present in the text, return an empty list or empty string for it.
Do not invent information that is not in the text.
"""

def analyze_jd(jd_text: str) -> dict:
    """
    Sends job description text to the LLM and returns structured data.
    Tries each model in MODELS in order, falling back if one is
    unavailable, rate-limited, or errors out.
    
    Args:
        jd_text: job description text (pasted or extracted)
    
    Returns:
        A dictionary with job_title, required_skills, preferred_skills,
        responsibilities, qualifications, keywords
    
    Raises:
        RuntimeError: if every model in the fallback chain fails
    """
    last_error = None
    
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": JD_ANALYSIS_PROMPT},
                    {"role": "user", "content": jd_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            raw_output = response.choices[0].message.content
            parsed = json.loads(raw_output)
            
            print(f"✓ Success using model: {model_name}")
            return parsed
        
        except APIStatusError as e:
            print(f"✗ {model_name} failed ({e.status_code}), trying next model...")
            last_error = e
            continue
        
        except json.JSONDecodeError as e:
            print(f"✗ {model_name} returned invalid JSON, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")