# Libs imports
from pydantic import BaseModel
# Local imports
from models.user import PublicUser
from models.planning import Planning


class Company(BaseModel):
    id: int = None
    name: str
    website: str = None
    city: str
    country: str
    users: list[PublicUser] = []
    plannings: list[Planning] = []
    created_at: int = None
    updated_at: int = None


class CompanyChangeableFields(BaseModel):
    name: str = None
    website: str = None
    city: str = None
    country: str = None


class AddToCompany(BaseModel):
    userId: int
    companyId: int
