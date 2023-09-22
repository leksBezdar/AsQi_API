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

class TitleCreateDB(TitleBase):
    id: str

class TitleUpdate(BaseModel):
    name: Optional[str] = None
    trailer_link: Optional[str] = None
    num_episodes: Optional[int] = None
    synopsis: Optional[str] = None
    japanese_title: Optional[str] = None
    country: Optional[str] = None
    year: Optional[int] = None
    genres: Optional[Dict] = None
    rating: Optional[str] = None
    status: Optional[str] = None
    studio: Optional[str] = None
    MPAA: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None
    small_img: Optional[str] = None
    big_img: Optional[str] = None
    screens: Optional[Dict] = None

class Title(TitleBase):
    id: str

    class Config:
        from_attributes = True
        

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str
    translations: Dict
    title_id: str
    episode_number: int
    
    
    
class Episode(EpisodeBase):
    episode_number: int
        
        
class EpisodeCreate(EpisodeBase):
    title_id: str
    episode_title: Optional[str] = None

class EpisodeUpdate(BaseModel):
    episode_title: Optional[str] = None
    episode_link: Optional[str] = None
    translations: Optional[Dict] = None
    title_id: Optional[str] = None
    episode_number: Optional[int] = None