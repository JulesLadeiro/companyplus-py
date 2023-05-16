# Libs imports
from pydantic import BaseModel


class Planning(BaseModel):
    id: int = None
    name: str
    company_id: int
    created_at: int = None
    updated_at: int = None


class PlanningChangeableFields(BaseModel):
    name: str = None
    company_id: int = None
