from pydantic import BaseModel


class Session(BaseModel):
    location: dict[str, int]
