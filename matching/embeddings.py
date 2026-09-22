from sentence_transformers import SentenceTransformer

# Load once, reuse everywhere — loading this model is slow,
# so we don't want to reload it on every function call
_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    """
    Converts a piece of text into its embedding vector.
    
    Args:
        text: any phrase or sentence
    
    Returns:
        A numpy array representing the text's meaning as a vector
    """
    return _model.encode(text)