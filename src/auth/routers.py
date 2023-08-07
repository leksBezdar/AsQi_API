from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict


from . import crud
from . import schemas 
from ..database import get_async_session
from .auth import create_access_token, hash_password, validate_password


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

    access_token = create_access_token(data={"sub": user.username})
    user_dict = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "access_token": access_token,
    }

    return {"user": user_dict}