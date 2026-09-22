import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url: str) -> str:
    """
    Fetches a webpage and extracts its readable text content.
    
    Args:
        url: the job posting URL
    
    Returns:
        Plain text extracted from the page
    
    Raises:
        requests.HTTPError: if the page can't be fetched
    """
    headers = {
        "User-Agent": "Mozilla/5.0"   # some sites block requests without a browser-like header
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()   # raises an error if the request failed (404, 403, etc.)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove script and style tags — we don't want JS code or CSS as "text"
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n")
    
    # Collapse excessive blank lines that come from HTML's messy whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)