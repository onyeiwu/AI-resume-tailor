import pymupdf as pym  # alias — same library, shorter name to type

def extract_text_from_pdf(file_path: str) -> str:
    doc = pym.open(file_path)   # use the alias here too
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text