from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.future import select

from .models import Anime
from .schemas import AnimeCreate


# async def create_anime(session: AsyncSession, anime_data: AnimeCreate) -> Anime:
#     anime = Anime(**anime_data.model_dump())
#     session.add(anime)
#     await session.flush()
#     return anime


async def create_anime(db: AsyncSession, anime: AnimeCreate):
    db_anime = Anime(
        title=anime.title,
        trailer_link=anime.trailer_link,
        num_episodes=anime.num_episodes,
        synopsis=anime.synopsis
    )
    db.add(db_anime)
    await db.commit()
    await db.refresh(db_anime)
    return db_anime


async def get_anime_by_id(db: AsyncSession, anime_id: int = None, title: str = None):
    if not anime_id and not title:
        raise ValueError("Either 'anime_id' or 'title' must be provided.")

    stmt = select(Anime).where(
        or_(Anime.id == anime_id, Anime.title == title)
    )

    result = await db.execute(stmt)
    anime = result.scalar_one_or_none()

    if anime is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown ID or title"
            )

    return anime