import re

_ws = re.compile(r"\s+")

def clean_text(s: str) -> str:
    s = s or ""
    s = s.replace("\u00a0", " ")
    s = _ws.sub(" ", s).strip()
    return s
