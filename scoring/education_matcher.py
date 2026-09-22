# Ranks each education level so we can compare "is this high enough"
EDUCATION_RANK = {
    "none": 0,
    "unspecified": 0,
    "bachelor": 1,
    "master": 2,
    "phd": 3
}

def education_match(cv_education_level: str, jd_education_required: str) -> dict:
    """
    Compares a candidate's highest education level against the JD's requirement.
    
    Args:
        cv_education_level: highest_education_level from analyze_cv()
        jd_education_required: education_required from analyze_jd()
    
    Returns:
        A dict with a score (0-100), a status label, and a human-readable note
    """
    # Case 1: JD doesn't specify a requirement, or explicitly requires none
    if jd_education_required in (None, "none", "unspecified"):
        return {
            "score": 100,
            "status": "not_applicable",
            "note": "This job posting does not require a specific education level."
        }
    
    # Case 2: we couldn't determine the CV's education level
    if cv_education_level in (None, "unspecified"):
        return {
            "score": 50,
            "status": "unknown",
            "note": f"Job requires {jd_education_required}, but education level could not be determined from the CV. Recommend manual review."
        }
    
    cv_rank = EDUCATION_RANK.get(cv_education_level, 0)
    jd_rank = EDUCATION_RANK.get(jd_education_required, 0)
    
    # Case 3: candidate meets or exceeds the requirement
    if cv_rank >= jd_rank:
        return {
            "score": 100,
            "status": "meets_requirement",
            "note": f"Candidate's {cv_education_level} degree meets the {jd_education_required} requirement."
        }
    
    # Case 4: candidate falls short
    return {
        "score": 0,
        "status": "below_requirement",
        "note": f"Candidate has {cv_education_level}; job requires {jd_education_required}."
    }