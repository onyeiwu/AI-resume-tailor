from tailoring.tailor import tailor_summary
from tailoring.verify import verify_summary

def generate_verified_summary(cv_analysis: dict, jd_analysis: dict) -> dict:
    """
    Generates a tailored summary AND verifies it against the original data
    in one call. Nothing downstream should call tailor_summary() directly —
    always go through this function so verification can't be skipped.
    
    Args:
        cv_analysis: the full result dict from analyze_cv()
        jd_analysis: the full result dict from analyze_jd()
    
    Returns:
        A dict with the tailored summary, verification details, and a
        clear recommendation on whether it's safe to use as-is.
    """
    tailored_summary = tailor_summary(cv_analysis, jd_analysis)
    verification = verify_summary(cv_analysis, tailored_summary)
    
    if verification.get('has_unsupported_claims'):
        recommendation = "review_required"
    else:
        recommendation = "safe_to_use"
    
    return {
        "tailored_summary": tailored_summary,
        "recommendation": recommendation,
        "verification": verification
    }