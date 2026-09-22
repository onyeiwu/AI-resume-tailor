from interview.question_generator import generate_interview_questions
from tailoring.verify import verify_summary

def generate_verified_questions(cv_analysis: dict, jd_analysis: dict) -> dict:
    """
    Generates interview questions AND verifies the open-ended categories
    against the original CV data. MCQ categories (technical, role-specific)
    are lower fabrication risk since they're constrained by fixed options.
    
    Args:
        cv_analysis: the full result dict from analyze_cv()
        jd_analysis: the full result dict from analyze_jd()
    
    Returns:
        A dict with the questions, verification results, and a review note
    """
    questions = generate_interview_questions(cv_analysis, jd_analysis)
    
    # Only the open-ended categories carry real fabrication risk —
    # MCQ questions are constrained by fixed options, lower risk
    open_ended_text = "\n".join(
        questions.get('behavioral_questions', []) +
        questions.get('cv_based_questions', [])
    )
    verification = verify_summary(cv_analysis, open_ended_text)
    
    return {
        "questions": questions,
        "verification": verification,
        "review_note": "AI-generated content — please verify all CV-based and behavioral questions against your actual experience before using them in interview prep."
    }