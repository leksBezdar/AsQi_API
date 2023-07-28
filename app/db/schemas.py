from pydantic import BaseModel

class AnimeBase(BaseModel):
    id: int
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str
    japanese_title: str
    country: str
    year: int
    genres: str
    rating: str
    type: str
    status: str
    studio: str
    MPAA: str
    type: str
    duration: int

class AnimeCreate(BaseModel):
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str
    japanese_title: str
    country: str
    year: int
    genres: str
    rating: str
    type: str
    status: str
    studio: str
    MPAA: str
    type: str
    duration: int

class Anime(AnimeBase):
    id: int

    class Config:
        from_attributes = True

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str
    translations: dict

class EpisodeCreate(EpisodeBase):
    pass

class Episode(EpisodeBase):
    id: int

    class Config:
        from_attributes = True
