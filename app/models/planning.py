# Libs imports
from pydantic import BaseModel


class Planning(BaseModel):
    id: int = None
    name: str
    company_id: int
    created_at: str = None
    updated_at: str = None


class PlanningChangeableFields(BaseModel):
    name: str = None
    company_id: int = None
