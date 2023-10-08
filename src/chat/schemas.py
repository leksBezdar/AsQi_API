from pydantic import BaseModel


class MessagesModel(BaseModel):
    user_id: str
    chat_id: int
    message: str

    class Config:
        from_attributes = True