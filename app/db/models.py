from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import MetaData

metadata = MetaData()

class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    trailer_link = Column(String, nullable=False)
    num_episodes = Column(Integer, nullable=False)
    synopsis = Column(String, nullable=False)
    
    episodes = relationship("Episode", back_populates="anime")

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    episode_title = Column(String, index=True, nullable=False)
    episode_link = Column(String, nullable=False)
    anime_id = Column(Integer, ForeignKey("animes.id"))

    anime = relationship("Anime", back_populates="episodes")
