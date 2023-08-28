from fastapi import HTTPException

class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Incorrect username or password")

class InvalidAuthenthicationCredential(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid authentication credential")

class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")

class TokenExpired(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token has expired")

class InactiveUser(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Inactive user")

class NotEnoughPermissions(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Not enough permissions")

class UserDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User does not exist")

class RoleDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Role does not exist")

class NoData(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Data was not found")

class NoUserData(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User data was not found")

class NoRoleData(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Role data was not found")

class TokenWasNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Token was not found")

class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already exists")

class RoleAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Role already exists")
        
class UserAlreadyActive(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User is already active")
