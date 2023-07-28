from pydantic import BaseModel

class AnimeBase(BaseModel):
    id: int
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str

class AnimeCreate(BaseModel):
    title: str
    trailer_link: str
    num_episodes: int
    synopsis: str

class Anime(AnimeBase):
    id: int

    class Config:
        from_attributes = True

class EpisodeBase(BaseModel):
    episode_title: str
    episode_link: str

class EpisodeCreate(EpisodeBase):
    pass

class Episode(EpisodeBase):
    id: int
    anime_id: int

    class Config:
        from_attributes = True

class AnimeMetadata(BaseModel):
    title: str
    synopsis: str
