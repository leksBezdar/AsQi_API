from pydantic import BaseModel
    

class AnimeBase(BaseModel):
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str
    japanese_title: str
    country: str
    year: int
    genres: dict
    rating: str
    status: str
    studio: str
    MPAA: str
    duration: int
    type: str
    small_img: str
    big_img: str
    screens: dict 
    

class Anime(AnimeBase):
    id: int

    class Config:
        from_attributes = True
        
    
        

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str
    translations: dict
    


class Episode(EpisodeBase):
    id: int

    class Config:
        from_attributes = True
