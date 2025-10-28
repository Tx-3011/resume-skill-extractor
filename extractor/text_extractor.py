import pdfplumber
from extractor.utils import clean_text

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.
    Works with uploaded files (BytesIO) or file paths.
    """
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)
