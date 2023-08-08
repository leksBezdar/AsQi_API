from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict

from .config import ALGORITHM, SECRET_KEY


from . import crud
from . import schemas 
from ..database import get_async_session
from .auth import create_tokens, hash_password, validate_password


router = APIRouter()



@router.post("/registration/", response_model=Dict[str, Any])
async def create_user(
    user_data: schemas.UserBase,
    db: AsyncSession = Depends(get_async_session),
):
    if await crud.get_existing_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
    ):
       raise HTTPException(status_code=409, detail='User already exists') 
   
    # Хеширование пароля перед сохранением
    salt = crud.get_random_string()
    hashed_password = hash_password(user_data.hashed_password, salt)
    user_data.hashed_password = f"{salt}${hashed_password}"
    
    created_user = await crud.create_user(db, user_data)
    
    
    user_dict = {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
    }
    
    return {"user":user_dict}


@router.post("/create_role/", response_model=schemas.RoleBase)
async def create_role(
    role_data: schemas.RoleBase,
    db: AsyncSession = Depends(get_async_session),
):
    if await crud.check_existing_role(
        db=db,
        role_name=role_data.name
    ):
        raise HTTPException(status_code=409, detail='Role already exists') 
    
    return await crud.create_role(db, role_data)


@router.patch("/update_user_role/")
async def patch_user_role(
    user_id: int,
    new_role_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    return await crud.update_user_role(db, user_id, new_role_id)


@router.get("/get_all_users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await crud.read_all_users(db=db, skip=skip, limit=limit)



@router.post("/login/", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not validate_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token, refresh_token = create_tokens(user)
    
    # Устанавливаем access токен как куку
    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response


@router.post("/refresh-tokens/", response_model=Dict[str, Any])
async def refresh_tokens(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = crud.get_user_by_username(db, username)
        if user is None or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        access_token, new_refresh_token = create_tokens(user)
        user.refresh_token = new_refresh_token
        await db.commit()

        return {"access_token": access_token, "refresh_token": new_refresh_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
