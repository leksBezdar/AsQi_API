from typing import Optional
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import OAuth2PasswordBearerWithCookie

from . import exceptions
from .models import User
from ..database import get_async_session
from .service import DatabaseManager


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/login")


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_async_session),
        token: str = Depends(oauth2_scheme),
):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    token_crud = db_manager.token_crud
    
    try:
        # access_token = request.cookies.get('access_token')
        user_id = await token_crud.get_access_token_payload(token)
        # user_id = await token_crud.get_access_token_payload(access_token)

    except KeyError:
        raise exceptions.InvalidCredentials
    
    print(user_id)
    
    user = await user_crud.get_existing_user(user_id=user_id)
    print(user)
    return user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise exceptions.NotEnoughPermissions
    return current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise exceptions.InactiveUser
    return current_user
    
    
        
    
