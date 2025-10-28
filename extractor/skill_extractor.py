import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

def extract_skills(text, skills_list):
    """
    Extracts known skills from text using PhraseMatcher.
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skills_list]
    matcher.add("SKILLS", patterns)

    doc = nlp(text)
    matches = matcher(doc)
    
    extracted = list(set([doc[start:end].text for _, start, end in matches]))
    return extracted
