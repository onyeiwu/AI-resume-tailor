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

VERIFICATION_PROMPT = """You are a strict fact-checker. You compare AI-generated text
(which may be a summary, bullet points, or interview questions) against a candidate's
ORIGINAL verified data, and identify any claim in the text that is NOT clearly supported
by the original data.

You only output valid JSON. Never include explanations outside the JSON structure.

Return this exact structure:
{
  "has_unsupported_claims": true or false,
  "unsupported_claims": ["specific phrase or claim from the text that isn't backed by the original data"],
  "reasoning": "brief explanation of what was flagged and why, or why nothing was flagged"
}

Be strict: if a specific method, technique, tool, number, or detail appears in the text
that is not explicitly present in the original data — even if it sounds plausible, is a
reasonable-sounding elaboration, or is phrased as a QUESTION rather than a statement —
flag it. IMPORTANT: a question can still contain a false claim in its setup. For example,
"You reduced AWS spend by 34%. What optimizations did you use?" makes a factual claim
("by 34%") even though it's phrased as a lead-in to a question — if "34%" doesn't appear
in the original data, this MUST be flagged. Do not give a pass to fabricated numbers,
tools, or techniques just because they appear inside a question's setup rather than a
plain statement.

A vague rephrasing of something real (e.g. "built software" -> "developed applications")
is fine and should NOT be flagged. A specific new detail (e.g. adding "using rightsizing"
to a real "reduced AWS spend" achievement, or adding a specific percentage/number not
stated in the original) SHOULD be flagged.
"""

def verify_summary(original_data: dict, generated_summary: str) -> dict:
    """
    Checks a generated summary against the candidate's real data for
    unsupported/fabricated claims.
    
    Args:
        original_data: the same structured CV data passed to tailor_summary()
        generated_summary: the LLM-generated summary text to check
    
    Returns:
        A dict with has_unsupported_claims, unsupported_claims, and reasoning
    """
    context = f"""
ORIGINAL VERIFIED DATA:
{json.dumps(original_data, indent=2)}

GENERATED SUMMARY TO CHECK:
{generated_summary}
"""
    
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": VERIFICATION_PROMPT},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except (APIStatusError, json.JSONDecodeError) as e:
            print(f"✗ {model_name} failed, trying next model...")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")


def verify_skills_reorder(original_skills: list, reordered_skills: list) -> dict:
    """
    Confirms a reordered skills list contains exactly the same skills
    as the original — no additions, removals, or renames. Pure logic,
    no LLM involved, so this check is 100% reliable.
    """
    original_set = set(original_skills)
    reordered_set = set(reordered_skills)
    
    added = reordered_set - original_set
    removed = original_set - reordered_set
    
    is_valid = (len(added) == 0 and len(removed) == 0)
    
    return {
        "is_valid": is_valid,
        "added_skills": list(added),
        "removed_skills": list(removed)
    }