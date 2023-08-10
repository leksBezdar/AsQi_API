import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any, List, Dict

from .config import ALGORITHM, SECRET_KEY


from . import crud, schemas, auth, exceptions
from ..database import get_async_session
from .auth import create_tokens, hash_password, validate_password


router = APIRouter()



@router.post("/registration/", response_model=Dict[str, Any])
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_async_session),
):
    if await crud.get_existing_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
    ):
       raise exceptions.UserAlreadyExists
   
    # Хеширование пароля перед сохранением
    salt = auth.get_random_string()
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
    if await crud.get_existing_role(
        db=db,
        role_name=role_data.name
    ):
        raise exceptions.RoleAlreadyExists
    
    return await crud.create_role(db, role_data)


@router.post("/login/", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not validate_password(form_data.password, user.hashed_password):
        raise exceptions.InvalidCredentials

    access_token, refresh_token = create_tokens(user)
    
    await crud.patch_refresh_token(db, user, refresh_token)

    # Устанавливаем access токен как куку
    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response


@router.post("/update_access_token/", response_model=Dict[str, Any])
async def update_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exceptions.InvalidToken
        
        user = await crud.get_user_by_username(db, username)
        if user is None or user.refresh_token != refresh_token:
            raise exceptions.InvalidToken


        # Создаем токен для последующей передачи (возможно необходимо сменить логику)
        new_access_token = create_tokens(user)[0]
        
        # Устанавливаем access токен как куку    
        response = JSONResponse(content={
        "message": "Updating successful",
        "new_access_token": new_access_token,
        "refresh_token": refresh_token,
    })
        response.set_cookie(key="access_token", value=new_access_token, httponly=True)

        return response

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpired
    except jwt.DecodeError:
        raise exceptions.InvalidToken



@router.get("/read_user_by_username")
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_async_session),
):
    user = crud.get_existing_user(db, username)
    if not user:
        raise exceptions.UserDoesNotExist
    
    return await crud.get_user_by_username(db, username)


@router.get("/read_user_by_email")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    print(1)
    user = crud.get_existing_user(db, email)
    if not user:
        raise exceptions.UserDoesNotExist
    
    return await crud.get_user_by_email(db, email)


@router.get("/read_user_by_id")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    user = crud.get_existing_user(db, user_id)
    if not user:
        raise exceptions.UserDoesNotExist
    
    return await crud.get_user_by_id(db, user_id)


@router.get("/read_all_users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await crud.read_all_users(db=db, skip=skip, limit=limit)

    
@router.patch("/update_user_role/")
async def patch_user_role(
    user_id: str,
    new_role_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    user = await crud.get_existing_user(db, user_id=user_id)
    role = await crud.get_existing_role(db, role_id=new_role_id)
    
    if not user:
        raise exceptions.UserDoesNotExist
    
    if not role:
        raise exceptions.RoleDoesNotExist
    
    new_user_role = await crud.update_user_role(db, user_id, new_role_id)
    return new_user_role
