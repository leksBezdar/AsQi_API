from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import crud
from . import schemas 
from ..database import get_async_session

router = APIRouter()


@router.post("/registration/", response_model=schemas.UserBase)
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
   
    return await crud.create_user(db, user_data)
        

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
async def get_all_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    return await crud.read_all_users(db=db, skip=skip, limit=limit)
