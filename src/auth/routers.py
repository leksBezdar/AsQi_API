import jwt

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any, List, Dict

from .config import ALGORITHM, JWT_SECRET_KEY


from . import schemas, exceptions, security
from ..database import get_async_session
from .security import create_tokens, hash_password, validate_password
from .crud import DatabaseManager
from .authorization import has_permissons


router = APIRouter()



# Регистрация нового пользователя
@router.post("/registration/", response_model=dict)
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud

    # Проверка на существующего пользователя по email и username
    user = await user_crud.get_existing_user(
        email=user_data.email,
        username=user_data.username,
    )

    if user:
        raise exceptions.UserAlreadyExists

    # Хеширование пароля перед сохранением
    salt = await security.get_random_string()
    hashed_password = await hash_password(user_data.hashed_password, salt)
    user_data.hashed_password = f"{salt}${hashed_password}"

    # Создание нового пользователя
    created_user = await user_crud.create_user(user_data)

    # Подготовка данных для ответа
    user_dict = {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
    }

    return {"user": user_dict}


# Создание новой роли
@router.post("/create_role/", response_model=schemas.RoleBase)
async def create_role(
    role_data: schemas.RoleBase,
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    role_crud = db_manager.role_crud
    
    # Проверка на существующего пользователя по email и username
    if await role_crud.get_existing_role(
        role_name=role_data.name
    ):
        raise exceptions.RoleAlreadyExists
    
    return await role_crud.create_role(role_data)


# Точка входа пользователя
@router.post("/login/", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud

    user = await user_crud.get_user_by_username(form_data.username)
    if not user or not await validate_password(form_data.password, user.hashed_password):
        raise exceptions.InvalidCredentials

    access_token, refresh_token = await create_tokens(user)
    
    user_statement = await user_crud.update_user_statement(username=form_data.username)

    await user_crud.patch_refresh_token(user, refresh_token)

    response = JSONResponse(content={
        "message": "login successful",
    })
    
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response


# Точка обновления access токена
@router.post("/update_access_token/", response_model=Dict[str, Any])
async def update_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise exceptions.InvalidToken
        
        db_manager= DatabaseManager(db)
        user_crud = db_manager.user_crud
        user = await user_crud.get_user_by_username(username)
        
        if user is None or user.refresh_token != refresh_token:
            raise exceptions.InvalidToken

        new_access_token, _ = await create_tokens(user)
        
        response = JSONResponse(content={
            "message": "Updating successful",
        })
        
        response.set_cookie(key="access_token", value=new_access_token, httponly=True)

        return response

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpired
    
    except jwt.DecodeError:
        raise exceptions.InvalidToken


# Получение информации о пользователе по имени пользователя
@router.get("/read_user_by_username")
async def get_user_by_username(
    request: Request,
    username: str,
    db: AsyncSession = Depends(get_async_session),
):
    
    has_permissions = await has_permissons(user_role="admin", request=request, db=db)
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    user = await user_crud.get_user_by_username(username)
    
    if not user:
        raise exceptions.UserDoesNotExist
    
    return user


# Получение информации о пользователе по email
@router.get("/read_user_by_email")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    user = await user_crud.get_user_by_email(email)
    
    if not user:
        raise exceptions.UserDoesNotExist
    
    return user


# Получение информации о пользователе по ID
@router.get("/read_user_by_id")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    user = await user_crud.get_user_by_id(user_id)
    
    if not user:
        raise exceptions.UserDoesNotExist
    
    return user


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
    user_id: str,
    new_role_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    db_manager = DatabaseManager(db)
    
    user_crud = db_manager.user_crud
    role_crud = db_manager.role_crud
    
    user = await user_crud.get_user_by_id(user_id)
    role = await role_crud.get_role_by_id(new_role_id)
    
    if not user:
        raise exceptions.UserDoesNotExist
    
    if not role:
        raise exceptions.RoleDoesNotExist
    
    new_user_data = await user_crud.update_user_role(user_id, new_role_id)
    
    return new_user_data


# Точка выхода пользователя
@router.post("/logout/")
async def logout(request: Request, db: AsyncSession = Depends(get_async_session)):
    access_token = request.cookies.get('access_token')
    
    if not access_token: 
        raise exceptions.InactiveUser
     
    username = await security.get_token_payload(access_token)
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    user_statement = await user_crud.update_user_statement(username=username)
    
    response = JSONResponse(content={
        "message": "logout successful",
    })
        
    response.delete_cookie(key="access_token")
    
    return response