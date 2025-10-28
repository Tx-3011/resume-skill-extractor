import re

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, line breaks, and symbols.
    """
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII chars
    return text.strip()
