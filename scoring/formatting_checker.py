import re

def check_formatting(cv_text: str) -> dict:
    """
    Checks a resume's raw text for structural issues that could affect
    real-world ATS parsing — missing contact info, missing standard
    section headers, or unusual length.
    
    Args:
        cv_text: the raw extracted CV text
    
    Returns:
        A dict with a score (0-100), a list of issues found, and details
    """
    issues = []
    score = 100
    text_lower = cv_text.lower()
    
    # Check 1: email present
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', cv_text))
    if not has_email:
        issues.append("No email address detected — ATS systems may reject applications without contact info.")
        score -= 20
    
    # Check 2: phone number present (loose pattern — allows spaces, dashes, parens, + prefix)
    has_phone = bool(re.search(r'(\+?\d[\d\s\-\(\)]{7,}\d)', cv_text))
    if not has_phone:
        issues.append("No phone number detected.")
        score -= 10
    
    # Check 3: standard section headers present
    expected_sections = {
        "experience": ["experience", "work history", "employment"],
        "education": ["education", "academic"],
        "skills": ["skills", "expertise", "competencies"]
    }
    for section_name, keywords in expected_sections.items():
        if not any(kw in text_lower for kw in keywords):
            issues.append(f"No clear '{section_name.title()}' section header found.")
            score -= 15
    
    # Check 4: reasonable length
    word_count = len(cv_text.split())
    if word_count < 150:
        issues.append(f"Resume seems short ({word_count} words) — may be missing detail.")
        score -= 15
    elif word_count > 1500:
        issues.append(f"Resume seems long ({word_count} words) — some ATS systems truncate lengthy documents.")
        score -= 10
    
    score = max(0, score)
    
    return {
        "score": score,
        "issues": issues,
        "word_count": word_count
    }