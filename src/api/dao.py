from ..dao import BaseDAO
from .models import Title, Episode
from .schemas import TitleCreate, EpisodeCreate, TitleUpdate, EpisodeUpdate


class TitleDAO(BaseDAO[Title, TitleCreate, TitleUpdate]):
    model = Title

class EpisodeDAO(BaseDAO[Episode, EpisodeCreate, EpisodeUpdate]):
    model = Episode