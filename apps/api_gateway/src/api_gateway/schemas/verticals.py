from pydantic import BaseModel


class VerticalOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
