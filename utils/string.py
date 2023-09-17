import unicodedata


def clean_trail_and_non_alphabit(text):
    if not text:
        return text
    text = text.strip().lower()
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
