def experience_match(cv_years, jd_years_required) -> dict:
    """
    Compares a candidate's years of experience against the JD's requirement.
    
    Args:
        cv_years: total_years_experience from analyze_cv() — may be None
        jd_years_required: years_required from analyze_jd() — may be None
    
    Returns:
        A dict with a score (0-100), a status label, and a human-readable note
    """
    # Case 1: JD doesn't specify a years requirement at all
    if jd_years_required is None:
        return {
            "score": 100,
            "status": "not_applicable",
            "note": "This job posting does not specify a years-of-experience requirement."
        }
    
    # Case 2: JD requires experience, but we couldn't determine the CV's years
    if cv_years is None:
        return {
            "score": 50,
            "status": "unknown",
            "note": f"Job requires {jd_years_required}+ years, but years of experience could not be determined from the CV. Recommend manual review."
        }
    
    # Case 3: both numbers exist — do the real comparison
    if cv_years >= jd_years_required:
        return {
            "score": 100,
            "status": "meets_requirement",
            "note": f"Candidate has {cv_years} years, meeting the {jd_years_required}+ year requirement."
        }
    else:
        gap = jd_years_required - cv_years
        score = max(0, 100 - (gap * 25))
        return {
            "score": round(score, 1),
            "status": "below_requirement",
            "note": f"Candidate has {cv_years} years; job requires {jd_years_required}+ years (gap of {gap})."
        }