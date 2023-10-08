from sqlalchemy import Column, Integer, String

from ..database import Base


class Messages(Base):
    __tablename__ = "messages"

    user_id = Column(String, primary_key=True)
    chat_id = Column(Integer, unique=True)
    message = Column(String)