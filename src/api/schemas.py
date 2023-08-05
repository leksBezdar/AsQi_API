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
    duration: int
    type: str
    small_img: str
    big_img: str
    screens: Dict 
    

class Anime(AnimeBase):
    id: int

    class Config:
        from_attributes = True
        
    
        

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str
    translations: Dict
    


class Episode(EpisodeBase):
    id: int
    anime_id: int

    class Config:
        from_attributes = True
