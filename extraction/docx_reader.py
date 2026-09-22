import docx  # python-docx — installed as 'python-docx', imported as 'docx'

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts raw text from a DOCX file.
    
    Args:
        file_path: path to the DOCX file on disk
    
    Returns:
        A single string containing all paragraph text from the document.
    """
    doc = docx.Document(file_path)   # loads the docx structure
    
    full_text = []
    for paragraph in doc.paragraphs:   # a docx is a sequence of paragraphs
        full_text.append(paragraph.text)
    
    return "\n".join(full_text)