# Libs imports
from pydantic import BaseModel


class UserEventInfo(BaseModel):
    id: int
    first_name: str = None
    last_name: str = None
    email: str = None
    role: str
    accepted: bool = None
    added_at: int = None
    accepted_at: int = None


class Event(BaseModel):
    id: int = None
    name: str
    place: str
    start_date: int
    end_date: int
    planning_id: int
    users: list[UserEventInfo] = []
    owner_id: int
    company_id: int = None
    created_at: int = None
    updated_at: int = None


class EventChangeableFields(BaseModel):
    name: str = None
    place: str = None
    start_date: int = None
    end_date: int = None
    planning_id: int = None


class DefaultResponse(BaseModel):
    success: bool
