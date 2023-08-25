from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

from . import schemas, security

from .models import User, Role
from .service import DatabaseManager
from ..database import get_async_session


router = APIRouter()



# Регистрация нового пользователя
@router.post("/registration/", response_model=schemas.User)
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_async_session),
) -> User:
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.create_user(user=user_data)


# Создание новой роли
@router.post("/create_role/", response_model=schemas.RoleBase)
async def create_role(
    role_data: schemas.RoleBase,
    db: AsyncSession = Depends(get_async_session),
) -> Role:
    
    db_manager = DatabaseManager(db)
    role_crud = db_manager.role_crud
    
    return await role_crud.create_role(role=role_data)


# Точка входа пользователя
@router.post("/login/")
async def login(
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    token_crud = db_manager.token_crud

    user = await user_crud.authenticate_user(username=credentials.username, password=credentials.password)
    
    # Создаем токены
    access_token, refresh_token = await token_crud.create_tokens(db=db, user_id=user.id)
    
    # Меняем состояние поля is_active пользователя
    await user_crud.update_user_statement(username=credentials.username)

    response = JSONResponse(content={
        "message": "login successful",
    })
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True)
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 30 * 24* 60,
        httponly=True)
    
    return response



# Точка выхода пользователя
@router.post("/logout/")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_session)
):
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')
   
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    await user_crud.logout(acces_token=access_token, refresh_token=refresh_token)
    
    response = JSONResponse(content={
        "message": "logout successful",
    })
        
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return response


# Получение информации о пользователе по имени пользователя
@router.get("/read_user")
async def get_user(
    username: str = None,
    email: str = None,
    user_id: str = None,
    db: AsyncSession = Depends(get_async_session),
):

    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    user = await user_crud.get_existing_user(username=username, email=email, user_id=user_id)

    return user or {"message": "No user found"}


# Получение списка всех пользователей
@router.get("/read_all_users", response_model=List[schemas.User])
async def get_all_users(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.get_all_users(offset=offset, limit=limit)


# Обновление роли пользователя
@router.patch("/update_user_role/")
async def patch_user_role(
    new_role_id: int,
    db: AsyncSession = Depends(get_async_session),
    username: str = None,
    user_id: str = None,
):
    db_manager = DatabaseManager(db)
    
    user_crud = db_manager.user_crud
    role_crud = db_manager.role_crud
    
    user = await user_crud.get_existing_user(username=username, user_id=user_id)
    new_role = await role_crud.get_existing_role(role_id = new_role_id)
    
    return await user_crud.update_user_role(user_id=user.id, new_role_id=new_role.id)


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    access_token, refresh_token = await user_crud.refresh_token(request.cookies.get("refresh_token"))

    response.set_cookie(
        'access_token',
        access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 7 * 24 * 60,
        httponly=True,
    )
    
    
    return access_token, refresh_token