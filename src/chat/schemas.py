from pydantic import BaseModel


class MessagesModel(BaseModel):
    id: int
    message: str

    class Config:
        from_attributes = True