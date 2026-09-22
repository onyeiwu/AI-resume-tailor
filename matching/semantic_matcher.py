from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from matching.embeddings import get_embedding

def semantic_similarity(phrase1: str, phrase2: str) -> float:
    """
    Computes how semantically similar two phrases are, using embeddings.
    
    Args:
        phrase1, phrase2: two phrases to compare
    
    Returns:
        A similarity score between -1 and 1 (practically, usually 0 to 1
        for related text)
    """
    vec1 = get_embedding(phrase1).reshape(1, -1)
    vec2 = get_embedding(phrase2).reshape(1, -1)
    
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return float(similarity)


#=================================================================
# This code is the second semantic_similarity for both the CV & JOB
#=================================================================

def semantic_skill_match(cv_skills: list, jd_skills: list, threshold: float = 0.5) -> dict:
    """
    For each JD skill, finds the best semantic match among CV skills.
    
    Args:
        cv_skills: list of skills from the CV
        jd_skills: list of required/preferred skills from the JD
        threshold: minimum similarity score to count as a match
    
    Returns:
        A dict showing matched pairs (with scores) and still-missing JD skills
    """
    matched = []
    missing = []
    
    for jd_skill in jd_skills:
        best_score = 0
        best_cv_skill = None
        
        for cv_skill in cv_skills:
            score = semantic_similarity(jd_skill, cv_skill)
            if score > best_score:
                best_score = score
                best_cv_skill = cv_skill
        
        if best_score >= threshold:
            matched.append({
                "jd_skill": jd_skill,
                "matched_cv_skill": best_cv_skill,
                "similarity": round(best_score, 2)
            })
        else:
            missing.append(jd_skill)
    
    match_percentage = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
    
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": round(match_percentage, 1)
    }