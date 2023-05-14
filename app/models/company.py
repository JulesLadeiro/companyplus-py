# Libs imports
from pydantic import BaseModel
# Local imports
from models.user import User
from models.planning import Planning


class Company(BaseModel):
    id: int = None
    name: str
    website: str = None
    city: str
    country: str
    users: list[User] = []
    plannings: list[Planning] = []
    created_at: str = None
    updated_at: str = None


class CompanyChangeableFields(BaseModel):
    name: str = None
    website: str = None
    city: str = None
    country: str = None


class AddToCompany(BaseModel):
    userId: int
    companyId: int
