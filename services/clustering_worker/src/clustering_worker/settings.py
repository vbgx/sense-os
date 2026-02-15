from pydantic import BaseModel

class Settings(BaseModel):
    batch_size: int = 200
