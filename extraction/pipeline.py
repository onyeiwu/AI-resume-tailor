from extraction.pdf_reader import extract_text_from_pdf
from extraction.docx_reader import extract_text_from_docx
from extraction.text_cleaner import fix_hyphenation

def process_pdf(file_path: str) -> str:
    """
    Full pipeline for a PDF: extract raw text, then clean it.
    """
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = fix_hyphenation(raw_text)
    return cleaned_text

def process_docx(file_path: str) -> str:
    """
    Full pipeline for a DOCX: extract raw text, then clean it.
    """
    raw_text = extract_text_from_docx(file_path)
    cleaned_text = fix_hyphenation(raw_text)
    return cleaned_text


import os

def process_resume(file_path: str) -> str:
    """
    Routes a resume file to the correct extraction pipeline based on
    its file extension.
    
    Args:
        file_path: path to a .pdf or .docx file
    
    Returns:
        Cleaned, ready-to-use text
    
    Raises:
        ValueError: if the file type isn't supported
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    if extension == ".pdf":
        return process_pdf(file_path)
    elif extension == ".docx":
        return process_docx(file_path)
    else:
        raise ValueError(f" The file you uploaded is Unsupported file type: {extension}. Only .pdf and .docx are supported.")