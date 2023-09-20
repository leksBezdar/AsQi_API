from pydantic import BaseModel
from typing import Dict, Optional
    

class TitleBase(BaseModel):
    name: str
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
    
class TitleCreate(TitleBase):
    pass

class TitleUpdate(BaseModel):
    pass

class Title(TitleBase):
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
    episode_title: Optional[str] = None

class EpisodeUpdate(BaseModel):
    pass