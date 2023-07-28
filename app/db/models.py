from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import MetaData

metadata = MetaData()


class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False, unique=True)
    japanese_title = Column(String, index=True, nullable=False)
    trailer_link = Column(String, nullable=False)
    num_episodes = Column(Integer, nullable=False)
    synopsis = Column(String, nullable=False)
    country = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    genres = Column(JSON, nullable=False)
    rating = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    studio = Column(String, nullable=False)
    MPAA = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    big_img = Column(String, nullable=False)
    small_img = Column(String, nullable=False)
    screens = Column(JSON, nullable=False)
    
    
    episodes = relationship("Episode", back_populates="anime")
    img = relationship("Image", back_populates="anime", uselist=False)


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    episode_title = Column(String, index=True, nullable=False)
    episode_link = Column(String, nullable=False)
    anime_id = Column(Integer, ForeignKey("animes.id"))
    translations = Column(JSON, nullable=False)

    anime = relationship("Anime", back_populates="episodes")
    
