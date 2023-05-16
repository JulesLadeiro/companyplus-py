# Libs imports
from pydantic import BaseModel


class UserEventInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    accepted = bool
    added_at = int
    accepted_at = int


class Event(BaseModel):
    id: int = None
    name: str
    place: str
    start_date: int
    end_date: int
    planning_id: int
    members_nb: int
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


class InviteToEvent(BaseModel):
    userId: int = None
    eventId: int


class DefaultResponse(BaseModel):
    success: bool
