import re

def fix_hyphenation(text: str) -> str:
    """
    Rejoins words that were split across a line break with a hyphen,
    e.g. 'Mathemat-\nics' becomes 'Mathematics'.
    
    Args:
        text: raw extracted text, possibly containing line-wrap hyphenation
    
    Returns:
        Text with hyphenated line-breaks rejoined.
    """
    # Pattern: a letter, hyphen, newline, then a lowercase letter
    pattern = r'([a-zA-Z])-\n([a-z])'
    
    # Replace: drop the hyphen and newline, join the letters directly
    cleaned = re.sub(pattern, r'\1\2', text)
    
    return cleaned