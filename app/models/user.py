# System imports
from enum import Enum
# Libs imports
from pydantic import BaseModel

# declare role enum


class UserRole(str, Enum):
    user = "USER"
    admin = "ADMIN"
    maintainer = "MAINTAINER"


class PublicUser(BaseModel):
    id: int = None
    first_name: str
    last_name: str
    role: UserRole


class User(PublicUser):
    email: str = None
    created_at: int = None
    updated_at: int = None


class UserChangeableFields(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None
    password_hash: str = None
    role: UserRole = None
