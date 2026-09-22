from matching.keyword_matcher import keyword_match
from matching.exact_matcher import exact_skill_match
from matching.semantic_matcher import semantic_skill_match
from scoring.experience_matcher import experience_match
from scoring.education_matcher import education_match
from scoring.formatting_checker import check_formatting

# Final weights — matching the original 6-part plan exactly, no re-normalization needed
KEYWORD_WEIGHT = 0.30
SKILLS_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.10
RESPONSIBILITIES_WEIGHT = 0.10
FORMATTING_WEIGHT = 0.05

def calculate_ats_score(cv_text: str, cv_skills: list, jd_keywords: list, jd_required_skills: list,
                          cv_years: int, jd_years_required: int,
                          cv_education_level: str, jd_education_required: str,
                          cv_key_duties: list, jd_key_responsibilities: list) -> dict:
    """
    Calculates the COMPLETE ATS score across all six components:
    Keyword, Skills, Experience, Education, Responsibilities, and Formatting.
    """
    kw_result = keyword_match(cv_text, jd_keywords)
    
    exact_result = exact_skill_match(cv_skills, jd_required_skills)
    semantic_result = semantic_skill_match(cv_skills, jd_required_skills)
    skills_score = (exact_result['match_percentage'] + semantic_result['match_percentage']) / 2
    
    exp_result = experience_match(cv_years, jd_years_required)
    edu_result = education_match(cv_education_level, jd_education_required)
    
    resp_result = semantic_skill_match(
        cv_skills=cv_key_duties,
        jd_skills=jd_key_responsibilities,
        threshold=0.4
    )
    
    fmt_result = check_formatting(cv_text)
    
    overall_score = (
        kw_result['match_percentage'] * KEYWORD_WEIGHT +
        skills_score * SKILLS_WEIGHT +
        exp_result['score'] * EXPERIENCE_WEIGHT +
        edu_result['score'] * EDUCATION_WEIGHT +
        resp_result['match_percentage'] * RESPONSIBILITIES_WEIGHT +
        fmt_result['score'] * FORMATTING_WEIGHT
    )
    
    return {
        "overall_score": round(overall_score, 1),
        "is_partial_score": False,
        "note": "Complete ATS score across all six components.",
        "breakdown": {
            "keyword_match": kw_result['match_percentage'],
            "skills_match_blended": round(skills_score, 1),
            "experience_match": exp_result['score'],
            "experience_status": exp_result['status'],
            "experience_note": exp_result['note'],
            "education_match": edu_result['score'],
            "education_status": edu_result['status'],
            "education_note": edu_result['note'],
            "responsibilities_match": resp_result['match_percentage'],
            "formatting_score": fmt_result['score'],
            "formatting_issues": fmt_result['issues']
        },
        "missing_keywords": kw_result['missing'],
        "missing_skills": exact_result['missing'],
        "missing_responsibilities": resp_result['missing']
    }