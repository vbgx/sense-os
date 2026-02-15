from pydantic import BaseModel

class Settings(BaseModel):
    formula_version: str = "v1"
    windows_days: tuple[int, int, int] = (7, 30, 90)
