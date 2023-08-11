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



# Регистрация нового пользователя
@router.post("/registration/", response_model=Dict[str, Any])
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_async_session),
):
    # Проверка на существующего пользователя по email и username
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
    
    # Создание нового пользователя
    created_user = await crud.create_user(db, user_data)
    
    
    # Подготовка данных для ответа
    user_dict = {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
    }
    
    return {"user":user_dict}


# Создание новой роли
@router.post("/create_role/", response_model=schemas.RoleBase)
async def create_role(
    role_data: schemas.RoleBase,
    db: AsyncSession = Depends(get_async_session),
):
    # Проверка на существующего пользователя по email и username
    if await crud.get_existing_role(
        db=db,
        role_name=role_data.name
    ):
        raise exceptions.RoleAlreadyExists
    
    return await crud.create_role(db, role_data)


# Точка входа пользователя
@router.post("/login/", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    # Проверяем данные пользователя
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not validate_password(form_data.password, user.hashed_password):
        raise exceptions.InvalidCredentials

    # Создаем токены для пользователя
    access_token, refresh_token = create_tokens(user)
    
    await crud.patch_refresh_token(db, user, refresh_token)

    # Подготовка ответа с информацией о успешном обновлении
    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    
    # Устанавливаем токен как куку
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response


# Точка обновления access токена
@router.post("/update_access_token/", response_model=Dict[str, Any])
async def update_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        # Декодирование refresh токена для извлечения данных
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        # Проверка наличия имени пользователя в токене
        if username is None:
            raise exceptions.InvalidToken
        
        # Получение информации о пользователе по имени
        user = await crud.get_user_by_username(db, username)
        
        # Проверка наличия пользователя и соответствия refresh токена
        if user is None or user.refresh_token != refresh_token:
            raise exceptions.InvalidToken

        # Создание нового access токена для последующей передачи
        new_access_token = create_tokens(user)[0]
        
        # Подготовка ответа с информацией о успешном обновлении и новым access токеном
        response = JSONResponse(content={
            "message": "Updating successful",
            "new_access_token": new_access_token,
            "refresh_token": refresh_token,
        })
        
        # Установка нового access токена как куки в ответе
        response.set_cookie(key="access_token", value=new_access_token, httponly=True)

        return response

    # Обработка исключения при истечении срока действия токена
    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpired
    
    # Обработка исключения при некорректном декодировании токена
    except jwt.DecodeError:
        raise exceptions.InvalidToken



# Получение информации о пользователе по имени пользователя
@router.get("/read_user_by_username")
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_async_session),
):
    # Получение пользователя с указанным именем
    user = crud.get_existing_user(db, username)
    
    # Проверка наличия пользователя
    if not user:
        raise exceptions.UserDoesNotExist
    
    # Возврат информации о пользователе
    return await crud.get_user_by_username(db, username)


# Получение информации о пользователе по email
@router.get("/read_user_by_email")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    # Получение пользователя с указанным email
    user = crud.get_existing_user(db, email)
    
    # Проверка наличия пользователя
    if not user:
        raise exceptions.UserDoesNotExist
    
    # Возврат информации о пользователе
    return await crud.get_user_by_email(db, email)


# Получение информации о пользователе по ID
@router.get("/read_user_by_id")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    # Получение пользователя с указанным ID
    user = crud.get_existing_user(db, user_id)
    
    # Проверка наличия пользователя
    if not user:
        raise exceptions.UserDoesNotExist
    
    # Возврат информации о пользователе
    return await crud.get_user_by_id(db, user_id)


# Получение списка всех пользователей
@router.get("/read_all_users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    # Получение списка пользователей с учетом пагинации
    return await crud.read_all_users(db=db, skip=skip, limit=limit)


# Обновление роли пользователя
@router.patch("/update_user_role/")
async def patch_user_role(
    user_id: str,
    new_role_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    # Получение пользователя по ID
    user = await crud.get_existing_user(db, user_id=user_id)
    
    # Получение роли по ID
    role = await crud.get_existing_role(db, role_id=new_role_id)
    
    # Проверка наличия пользователя
    if not user:
        raise exceptions.UserDoesNotExist
    
    # Проверка наличия роли
    if not role:
        raise exceptions.RoleDoesNotExist
    
    # Обновление роли пользователя
    new_user_role = await crud.update_user_role(db, user_id, new_role_id)
    
    # Возврат новой информации о пользователе с обновленной ролью
    return new_user_role
