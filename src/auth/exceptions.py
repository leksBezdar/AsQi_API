from fastapi import HTTPException

class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already exists")
        
class UserDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User does not exists")
        
class RoleDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Role does not exists")
        
class NoData(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Data was not found")

class RoleAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Role already exists")

class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Incorrect username or password")

class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")

class TokenExpired(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token has expired")
