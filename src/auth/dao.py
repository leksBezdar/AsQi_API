from .models import User, Role, Refresh_token
from .schemas import RefreshSessionCreate, RefreshSessionUpdate, RoleCreate, UserCreateDB, UserUpdate, RoleUpdate
from ..dao import BaseDAO


class UserDAO(BaseDAO[User, UserCreateDB, UserUpdate]):
    model = User

class RoleDAO(BaseDAO[Role, RoleCreate, RoleUpdate]):
    model = Role
    
class RefreshTokenDAO(BaseDAO[Refresh_token, RefreshSessionCreate, RefreshSessionUpdate]):
    model = Refresh_token
    