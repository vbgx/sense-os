from domain.scoring.language_detect_v0 import detect_language_code


def detect_language(content: str) -> str:
    return detect_language_code(text=content)
