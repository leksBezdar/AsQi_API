from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .security import get_current_user, get_token_payload
from ..database import get_async_session
from .crud import get_user_role


async def is_admin(request: Request, db: AsyncSession = Depends(get_async_session)):
    
    access_token = request.cookies.get('access_token')
    
    username = await get_token_payload(access_token)
    
    current_user_role = await get_user_role(db=db, username=username)
    
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return current_user_role