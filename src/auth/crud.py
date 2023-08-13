from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update


from .models import User, Role
from . import schemas, models, exceptions, auth


# Создание пользователя в базе данных
async def create_user(db: AsyncSession, user: schemas.UserBase):
    
    # Генерация уникального идентификатора пользователя с длинной от 8 до 12 символов
    id = await auth.get_random_user_id(user.email)
    
    # Создание объекта пользователя для сохранения в БД
    db_user = User(
        id=id,
        email=user.email, 
        username=user.username,              
        hashed_password=user.hashed_password, 
        is_active=False,       
        is_superuser=False,
        is_verified=False,
    )  
    
    # Добавление и сохранение пользователя в БД, *АТОМАРНОСТЬ
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


#Создание роли в базе данных
async def create_role(db: AsyncSession, role: schemas.RoleBase):
    
    # Создание объекта роли для сохранения в БД
    db_role = Role(
        name=role.name,
        is_active_subscription=role.is_active_subscription,
        permissions=role.permissions,
    )
    
    # Добавление и сохранение пользователя в БД, *АТОМАРНОСТЬ
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    
    return db_role


# Получение информации о пользователе по email
async def get_user_by_email(db: AsyncSession, user_email: str):
    
    """ Возвращает информацию о пользователе по email """
    
    stmt = select(User).where(User.email == user_email)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
     
    return user


# Получение информации о пользователе по username
async def get_user_by_username(db: AsyncSession, username: str):
    
    """ Возвращает информацию о пользователе по имени """
    # print(username)
    
    stmt = select(User).where(User.username == username)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # print(user)
    
    return user


# Получение информации о пользователе по id
async def get_user_by_id(db: AsyncSession, user_id: str):
    
    """ Возвращает информацию о пользователе по имени """
    
    stmt = select(User).where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    return user


async def get_user_by_token(db: AsyncSession, refresh_token: str):
    
    """ Возвращает информацию о пользователе по имени """
    
    if not refresh_token: 
        raise exceptions.TokenWasNotFount
    
    stmt = select(User).where(User.refresh_token == refresh_token)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    return user


# Получение информации о существовании пользователя в БД
async def get_existing_user(db: AsyncSession, email: str = None , username: str = None, user_id: str = None):
    
    """ Проверка на существующего пользователя """
    
    if email is None and username is None and user_id == None:
        raise exceptions.NoData()
    
    email_exists = await get_user_by_email(db, email)
    username_exists = await get_user_by_username(db, username)
    id_exists = await get_user_by_id(db, user_id)
    
    return email_exists or username_exists or id_exists


# Получение данных роли по role_name
async def get_role_by_name(db: AsyncSession, role_name: int):
    
    """ Возвращает информацию о роли по имени """
    
    Query = select(Role).where(Role.name == role_name)
    
    result = await db.execute(Query)
    role = result.scalar_one_or_none()
    
    return role


# Получение данных роли по role_id
async def get_role_by_id(db: AsyncSession, role_id: int):
    
    """ Возвращает информацию о роли по айди"""
    
    query = select(Role).where(Role.id == role_id)
    
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    
    return role


# Получение информации о существовании роли в БД
async def get_existing_role(db: AsyncSession, role_name: str = None, role_id: int = None):
    
    """ Возвращает информацию о существующей роли пользователе """
    
    if not role_name and not role_id:
        raise exceptions.NoRoleData()
    
    role_id_exists = await get_role_by_id(db, role_id)
    role_name_exists = await get_role_by_name(db, role_name)
    
    return role_id_exists or role_name_exists


# Получение информации о всех пользователях
async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    
    query = select(User).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    return result.scalars().all()


# Смена refresh токена пользователя
async def patch_refresh_token(db: AsyncSession, user: models.User, new_refresh_token: str):
    
    user.refresh_token = new_refresh_token
    await db.commit()
    
    return user


async def update_user_statement(db: AsyncSession, username: str = None, user_id: str = None):
    
    # Проверяем входные данные
    if not username and not user_id:
        raise exceptions.NoUserData
    
    # Поиск пользователя
    query = select(User.is_active).where(or_(User.username == username, User.id == user_id))
    result = await db.execute(query)
    is_active_stmt = result.fetchone()
    
    # Переключаем значение между True и False
    new_is_active = not is_active_stmt[0]
    
    # Обновление состояния поля is_active пользователя
    update_stmt = (
            update(User)
            .where(or_(User.username == username, User.id == user_id))
            .values(is_active=new_is_active)
            .returning(User.is_active)
        )
    result = await db.execute(update_stmt)
    await db.commit()
    
    return {"message": new_is_active}


# Смена роли пользователя
async def update_user_role(db: AsyncSession, user_id: str, new_role_id: int):
    
    """ Меняет роль пользователя """
    
    # Меняем роль пользователя
    stmt = update(User).where(User.id == user_id).values(role_id=new_role_id)
    await db.execute(stmt)
    
    # Получаем новую рольроль  
    query = select(Role).where(Role.id == new_role_id)

    result = await db.execute(query)
    new_user_data = result.scalar_one_or_none()
    
    return new_user_data
    
    

    