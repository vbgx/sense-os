import re

QUESTION_RE = re.compile(
    r"\?$|^(how|why|what|which|where|when|anyone|does anyone|is there)\b",
    re.I,
)
