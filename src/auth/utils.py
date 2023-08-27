import hashlib
import random
import string


# Генерация случайной строки заданной длины
async def get_random_string(length=16):
    
    """ Генерирует случайную строку, использующуюся как соль """
    
    return "".join(random.choice(string.ascii_letters) for _ in range(length))

    

# Проверка пароля на соответствие хешированному паролю
async def validate_password(password: str, hashed_password: str):
    
    """ Проверяет, что хеш пароля совпадает c хешем из БД """
    
    # Разделение хеша пароля на соль и хешированную часть
    salt, hashed = hashed_password.split("$")
    
    # Сравнение хешированного пароля
    return await hash_password(password, salt) == hashed


# Метод для хеширования пароля с учетом соли
async def hash_password(password: str, salt: str = None):
    
    """ Хеширует пароль c солью """
    
    # Если соль не указана, генерируем случайную соль
    if salt is None:
        salt = await get_random_string()
        
    # Применение хэш-функции PBKDF2 к паролю и соли
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)

    return enc.hex()