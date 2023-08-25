from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime


from .security import get_access_token_payload, get_refresh_token_payload
from ..database import get_async_session
from .crud import DatabaseManager



# async def has_permissions(required_role: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    
#     db_manager = DatabaseManager(db)
#     user_crud = db_manager.user_crud
#     role_crud = db_manager.role_crud
    
#     access_token = request.cookies.get('access_token')
    
#     username, expiration_time = await get_access_token_payload(access_token=access_token)
    
#     if not username and not expiration_time:
#         refresh_token = request.cookies.get('refresh_token')
#         username, expiration_time = await get_refresh_token_payload(refresh_token=refresh_token)
#         await update_user_tokens(refresh_token=refresh_token, db=db)
    

#     role_id = await user_crud.get_user_role_id(username=username)
#     current_user_role = await role_crud.get_role_by_id(role_id)
    
#     if required_role not in current_user_role:
#         raise HTTPException(status_code=403, detail="Permission denied")
    
#     return current_user_role


async def get_current_user(username: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    role_crud = db_manager.role_crud
    
    access_token = request.cookies.get('access_token')
    
    username, expiration_time = await get_access_token_payload(access_token=access_token)
    
