from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from . import schemas, security

from .models import User, Role
from .crud import DatabaseManager
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

    user = await user_crud.authenticate_user(username=credentials.username, password=credentials.password)
    
    # Создаем токены
    access_token, refresh_token = await security.create_tokens(user)
    
    # Меняем состояние поля is_active пользователя
    await user_crud.update_user_statement(username=credentials.username)

    # Устанавливаем токены пользователя: refresh_token в бд, куки; acces_token в куки
    await user_crud.patch_refresh_token(user, refresh_token)

    response = JSONResponse(content={
        "message": "login successful",
    })
    
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    
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
    await user_crud.logout(request=request, acces_token=access_token, refresh_token=refresh_token)
    
    response = JSONResponse(content={
        "message": "logout successful",
    })
        
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return response


# Получение информации о пользователе по имени пользователя
@router.get("/read_user_by_username")
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.get_user_by_username(username)
    
    


# Получение информации о пользователе по email
@router.get("/read_user_by_email")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.get_user_by_email(email)
    



# Получение информации о пользователе по ID
@router.get("/read_user_by_id")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.get_user_by_id(user_id)


# Получение списка всех пользователей
@router.get("/read_all_users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    return await user_crud.get_all_users(skip=skip, limit=limit)


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
    new_role = await role_crud.get_role_by_id(new_role_id)
    
    return await user_crud.update_user_role(user_id=user.id, new_role_id=new_role.id)