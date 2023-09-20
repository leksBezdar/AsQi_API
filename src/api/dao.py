from ..dao import BaseDAO
from .models import Anime, Episode
from .schemas import AnimeCreate, EpisodeCreate, AnimeUpdate, EpisodeUpdate


class AnimeDAO(BaseDAO[Anime, AnimeCreate, AnimeUpdate]):
    model = Anime

class EpisodeDAO(BaseDAO[Episode, EpisodeCreate, EpisodeUpdate]):
    model = Episode