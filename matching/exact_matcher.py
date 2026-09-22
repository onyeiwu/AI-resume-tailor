def normalize(text: str) -> str:
    """
    Lowercases and strips whitespace so comparisons aren't
    thrown off by casing or stray spaces.
    """
    return text.strip().lower()

def exact_skill_match(cv_skills: list, jd_skills: list) -> dict:
    """
    Compares CV skills against JD skills using exact (normalized) matching.
    
    Args:
        cv_skills: list of skills extracted from the CV
        jd_skills: list of skills extracted from the JD (required or preferred)
    
    Returns:
        A dict with matched skills, missing skills, and a match percentage
    """
    # Normalize both lists into sets for fast comparison
    cv_set = {normalize(skill) for skill in cv_skills}
    jd_set = {normalize(skill) for skill in jd_skills}
    
    matched = jd_set & cv_set        # intersection: skills present in both
    missing = jd_set - cv_set        # skills the JD wants but CV doesn't have
    
    match_percentage = (len(matched) / len(jd_set) * 100) if jd_set else 0
    
    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "match_percentage": round(match_percentage, 1)
    }