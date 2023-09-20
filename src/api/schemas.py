from pydantic import BaseModel
from typing import Dict
    

class AnimeBase(BaseModel):
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str
    japanese_title: str
    country: str
    year: int
    genres: Dict
    rating: str
    status: str
    studio: str
    MPAA: str
    duration: str
    type: str
    small_img: str
    big_img: str
    screens: Dict 
    
class AnimeCreate(AnimeBase):
    pass

class AnimeUpdate(BaseModel):
    pass

class Anime(AnimeBase):
    id: int

    class Config:
        from_attributes = True
        

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str
    translations: Dict
    anime_id: int
    
    
    
class Episode(EpisodeBase):
    episode_number: int
        
        
class EpisodeCreate(EpisodeBase):
    pass

class EpisodeUpdate(BaseModel):
    pass