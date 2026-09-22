def keyword_match(cv_text: str, jd_keywords: list) -> dict:
    """
    Checks how many JD keywords appear literally in the CV's raw text.
    
    Args:
        cv_text: the full raw CV text (not the structured skills list)
        jd_keywords: list of keywords from the JD analysis
    
    Returns:
        A dict with matched keywords, missing keywords, and match percentage
    """
    cv_text_lower = cv_text.lower()
    
    matched = []
    missing = []
    
    for keyword in jd_keywords:
        if keyword.lower() in cv_text_lower:
            matched.append(keyword)
        else:
            missing.append(keyword)
    
    match_percentage = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0
    
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": round(match_percentage, 1)
    }