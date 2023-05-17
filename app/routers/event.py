# System Imports
from typing import Annotated
import datetime
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from entities import Event as EventEntity, UserEvent as UserEventEntity, User as UserEntity, Planning as PlanningEntity, Company as CompanyEntity
from models.event import Event, EventChangeableFields, DefaultResponse
from models.user import User
from routers.user import get_user_by_id, get_users
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt, hash_password

router = APIRouter()


@router.get("/event")
async def get_event(wantedCompanyId: int = None, db: Session = Depends(get_db), authUser: Annotated[Event, Depends(decode_token)] = None) -> list[Event]:
    """
    Récupérer tout les événements de son entreprise.
    """
    show_all = False if authUser["role"] != "MAINTAINER" else True

    company_id = authUser["company_id"]
    if (authUser["role"] == "MAINTAINER"):
        company_id = None if not wantedCompanyId else wantedCompanyId
        if (company_id != None):
            db_company = db.query(CompanyEntity).filter_by(
                id=company_id).first()
            if (not db_company):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    if (company_id == None):
        db_events = db.query(EventEntity).outerjoin(PlanningEntity).all()
    else:
        db_events = db.query(EventEntity).outerjoin(PlanningEntity).filter_by(
            company_id=company_id).all()

    users = await get_users(db)

    db_events_dict = [event.__dict__ for event in db_events]
    for event in db_events_dict:
        planning = db.query(PlanningEntity).filter_by(
            id=event["planning_id"]).first().__dict__
        event["name"] = decrypt(event["name"])
        event["place"] = decrypt(event["place"])
        event["start_date"] = datetime.datetime.timestamp(event["start_date"])
        event["end_date"] = datetime.datetime.timestamp(event["end_date"])
        event["company_id"] = planning["company_id"]
        event["created_at"] = datetime.datetime.timestamp(event["created_at"])
        event["updated_at"] = datetime.datetime.timestamp(event["updated_at"])
        events_users = db.query(UserEventEntity).filter_by(
            event_id=event["id"]).all()
        events_users_dict = [
            event_user.__dict__ for event_user in events_users]
        event["users"] = []
        for event_user in events_users_dict:
            user = next(
                (user for user in users if user["id"] == event_user["user_id"]), None)
            user["accepted"] = event_user["accepted"]
            user["added_at"] = datetime.datetime.timestamp(
                event_user["added_at"])
            user["updated_at"] = datetime.datetime.timestamp(
                event_user["updated_at"])
            user["email"] = user["email"] if show_all else ""
            event["users"].append(user)

    return db_events_dict


@router.post("/event", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventChangeableFields, db: Session = Depends(get_db), authUser: Annotated[Event, Depends(decode_token)] = None) -> Event:
    """
    Créer une activité.
    """
    planning = db.query(PlanningEntity).filter_by(
        id=event.planning_id).first()
    if (planning == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Planning not found")
    if (planning.company_id != authUser["company_id"] and authUser["role"] != "MAINTAINER"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")

    try:
        startDate = datetime.datetime.fromtimestamp(event.start_date)
        endDate = datetime.datetime.fromtimestamp(event.end_date)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid date format, please use timestamp in seconds")

    if (startDate >= endDate):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Start date must be before end date")
    if (endDate - startDate < datetime.timedelta(minutes=15)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Event must last at least 15 minutes")

    db_event = EventEntity(
        name=encrypt(event.name),
        place=encrypt(event.place),
        start_date=startDate,
        end_date=endDate,
        planning_id=planning.id,
        owner_id=authUser["id"]
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    now = datetime.datetime.now()
    db_event_user_relation = UserEventEntity(
        event_id=db_event.id,
        user_id=authUser["id"],
        accepted=True,
        added_at=now,
        updated_at=now,
    )

    db.add(db_event_user_relation)
    db.commit()
    db.refresh(db_event_user_relation)

    user = await get_user_by_id(authUser["id"], db)

    db_event_decrypted = dict(
        id=db_event.id,
        name=decrypt(db_event.name),
        place=decrypt(db_event.place),
        start_date=datetime.datetime.timestamp(db_event.start_date),
        end_date=datetime.datetime.timestamp(db_event.end_date),
        planning_id=db_event.planning_id,
        owner_id=db_event.owner_id,
        users=[user],
        created_at=datetime.datetime.timestamp(db_event.created_at),
        updated_at=datetime.datetime.timestamp(db_event.updated_at)
    )

    return db_event_decrypted


@router.delete("/event/{eventId}")
async def delete_event_by_id(eventId: int, db: Session = Depends(get_db), authUser: Annotated[Event, Depends(decode_token)] = None) -> Event:
    """
    Supprimer un événement par son id, vous devez être le propriétaire de l'événement
    """

    old_event = db.query(EventEntity).filter_by(id=eventId).first()

    if (old_event == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")
    if (old_event.owner_id != authUser["id"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_event = db.query(EventEntity).filter_by(id=eventId).first()

    if db_event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")
    db.delete(db_event)
    db.commit()

    return old_event.__dict__


@router.patch("/event/{eventId}")
async def update_event_by_id(eventId: int, event: EventChangeableFields, db: Session = Depends(get_db), authUser: Annotated[Event, Depends(decode_token)] = None) -> Event:
    """
    Mettre à jour un événement par son id, vous devez être le propriétaire de l'événement
    """
    # Users with the role USER and ADMIN can't patch other users
    if (eventId != authUser["id"] and authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = db.query(EventEntity).filter_by(id=eventId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")

    db_user.first_name = encrypt(
        event.first_name) if event.first_name is not None else db_user.first_name
    db_user.last_name = encrypt(
        event.last_name) if event.last_name is not None else db_user.last_name
    db_user.email = encrypt(
        event.email) if event.email is not None else db_user.email
    db_user.password = hash_password(
        event.password) if event.password is not None else db_user.password
    db_user.role = event.role if event.role is not None else db_user.role
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)

    db_user_decrypted = dict(
        id=db_user.id,
        first_name=decrypt(db_user.first_name),
        last_name=decrypt(db_user.last_name),
        email=decrypt(db_user.email),
        role=db_user.role,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )

    return db_user_decrypted


@router.get("/event-add-user/{eventId}")
async def add_user_to_event(eventId: int, userId: int = None, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> DefaultResponse:
    """
    Ajouter un utilisateur à une activité,
    userId non requis si vous souhaitez vous ajouter vous-même.
    """
    userId = userId if userId else authUser["id"]

    db_user = db.query(UserEntity).filter_by(id=userId).first()
    db_event: Event = db.query(EventEntity).filter_by(id=eventId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    elif db_user.company_id != authUser["company_id"] and authUser["role"] != "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")
    elif db_event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")

    db_users_in_event = db.query(UserEventEntity).filter_by(
        event_id=eventId).all()
    userIsAlreadyInEvent = False
    for userEvent in db_users_in_event:
        if userEvent.user_id == db_user.id:
            userIsAlreadyInEvent = True
            break

    if userIsAlreadyInEvent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User is already in the event")

    db_planning = db.query(PlanningEntity).filter_by(
        id=db_event.planning_id).first()

    if db_planning == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The event is not in a planning")
    elif db_planning.company_id != authUser["company_id"] and authUser["role"] != "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")

    now = datetime.datetime.now()
    db_event_user = UserEventEntity(
        user_id=db_user.id,
        event_id=db_event.id,
        accepted=False if db_user.id != authUser["id"] else True,
        added_at=now,
        updated_at=now
    )

    db.add(db_event_user)
    db.commit()
    db.refresh(db_event_user)

    return {"success": True}


@router.get("/event-remove-user/{eventId}")
async def remove_user_from_event(eventId: int, userId: int = None, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> DefaultResponse:
    """
    Supprimer un utilisateur d'une activité,
    userId non requis si vous souhaitez vous supprimer vous-même.
    """
    userId = userId if userId else authUser["id"]

    db_user = db.query(UserEntity).filter_by(id=userId).first()
    db_event: Event = db.query(EventEntity).filter_by(id=eventId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    elif db_user.company_id != authUser["company_id"] and authUser["role"] != "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")
    elif db_event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")

    db_users_in_event = db.query(UserEventEntity).filter_by(
        event_id=eventId).all()
    userIsAlreadyInEvent = False
    for userEvent in db_users_in_event:
        if userEvent.user_id == db_user.id:
            userIsAlreadyInEvent = True
            break

    if not userIsAlreadyInEvent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User is not in the event")

    db_planning = db.query(PlanningEntity).filter_by(
        id=db_event.planning_id).first()

    if db_planning == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The event is not in a planning")
    elif db_planning.company_id != authUser["company_id"] and authUser["role"] != "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")

    db.query(UserEventEntity).filter_by(
        user_id=db_user.id, event_id=db_event.id).delete()
    db.commit()

    return {"success": True}


@router.get("/event-accept-invite/{eventId}")
async def accept_invite(eventId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> DefaultResponse:
    """
    Accepter une invitation à une activité
    """
    db_event: Event = db.query(EventEntity).filter_by(id=eventId).first()

    if db_event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Event not found")

    db_users_in_event = db.query(UserEventEntity).filter_by(
        event_id=eventId).all()
    userAlreadyAcceptedEvent = False
    for userEvent in db_users_in_event:
        if userEvent.user_id == authUser["id"] and userEvent.accepted == True:
            userAlreadyAcceptedEvent = True
            break

    if userAlreadyAcceptedEvent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="You've already accepted the event")

    db.query(UserEventEntity).filter_by(
        user_id=authUser["id"], event_id=db_event.id).update({UserEventEntity.accepted: True})
    db.commit()

    return {"success": True}
