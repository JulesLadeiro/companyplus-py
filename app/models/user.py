# System imports
from enum import Enum
# Libs imports
from pydantic import BaseModel


# declare role enum
class UserRole(str, Enum):
    user = "USER"
    admin = "ADMIN"
    maintainer = "MAINTAINER"


class User(BaseModel):
    id: int = None
    first_name: str
    last_name: str
    email: str
    password: str
    role: UserRole


class UserChangeableFields(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None
    password: str = None
    role: UserRole = None
