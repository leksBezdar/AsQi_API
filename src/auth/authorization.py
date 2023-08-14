from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .security import get_current_user, get_token_payload
from ..database import get_async_session
from .crud import DatabaseManager


async def is_admin(request: Request, db: AsyncSession = Depends(get_async_session)):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    role_crud = db_manager.role_crud
    
    access_token = request.cookies.get('access_token')
    
    username = await get_token_payload(access_token)
    
    role_id = await user_crud.get_user_role_id(username=username)
    
    current_user_role = await role_crud.get_role_by_id(role_id)
    
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return current_user_role