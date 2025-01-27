import re


def enforce_paragraph_format(text):
    cleaned_text = re.sub(r"[*+\-•]\s*", "", text)
    cleaned_text = re.sub(r"[\n\r]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    return cleaned_text.strip()
