# Libs imports
from pydantic import BaseModel
# Local imports
from models.user import User


class Company(BaseModel):
    id: int = None
    name: str
    email: str
    website: str = None
    city: str
    country: str
    users: list[User] = []
    created_at: str = None
    updated_at: str = None


class CompanyChangeableFields(BaseModel):
    name: str = None
    email: str = None
    website: str = None
    city: str = None
    country: str = None
