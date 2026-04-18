import re

def preprocess(text: str) -> str:
    """
    Clean medical text for NLP model.
    - Lowercase
    - Keep letters, digits, dots, slashes (for units like mg/dL)
    - Normalize whitespace
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.\-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
