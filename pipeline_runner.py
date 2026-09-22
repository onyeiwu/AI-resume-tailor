from extraction.pipeline import process_resume
from Ai_analyser.cv_analyzer import analyze_cv
from Ai_analyser.jd_analyzer import analyze_jd
from scoring.ats_score import calculate_ats_score

def run_full_analysis(cv_file_path: str, jd_text: str) -> dict:
    """
    Runs the entire pipeline end-to-end on any CV file and any JD text.
    """
    cv_text = process_resume(cv_file_path)
    result_cv = analyze_cv(cv_text)
    result_jd = analyze_jd(jd_text)
    
    score = calculate_ats_score(
        cv_text=cv_text,
        cv_skills=result_cv['skills'],
        jd_keywords=result_jd.get('keywords', []),
        jd_required_skills=result_jd['required_skills'],
        cv_years=result_cv.get('total_years_experience'),
        jd_years_required=result_jd.get('years_required'),
        cv_education_level=result_cv.get('highest_education_level'),
        jd_education_required=result_jd.get('education_required'),
        cv_key_duties=result_cv.get('key_duties', []),
        jd_key_responsibilities=result_jd.get('key_responsibilities', [])
    )
    
    return {
        "score": score,
        "cv_analysis": result_cv,
        "jd_analysis": result_jd
    }