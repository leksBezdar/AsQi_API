from typing import Optional
from fastapi import Depends, Request
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from . import exceptions
from .config import ALGORITHM, TOKEN_SECRET_KEY
from .models import User
from ..database import get_async_session
from .service import DatabaseManager



async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    token_crud = db_manager.token_crud
    
    refresh_token = request.cookies.get("refresh_token")
    user_id = await token_crud.get_refresh_token_payload(refresh_token)
    
    return await user_crud.get_existing_user(user_id=user_id)



async def get_current_superuser(current_user: User= Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise exceptions.NotEnoughPermissions
    return current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise exceptions.InactiveUser
    return current_user
    
    
        
    
