# System Imports
from typing import Annotated
import datetime
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session, contains_eager
from fastapi import Depends
# Local Imports
from models.planning import Planning, PlanningChangeableFields
from models.user import User
from entities import Planning as PlanningEntity
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt

router = APIRouter()


@router.get("/planning")
async def get_plannings(db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[Planning]:
    """
    Récupère tout les plannings de l'entreprise de l'utilisateur connecté
    """
    pass


@router.post("/planning", status_code=status.HTTP_201_CREATED)
async def create_planning(planning: PlanningChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Planning:
    """
    Créer un planning (ADMIN ou MAINTAINER)
    Les MAINTEINER peuvent créer des plannings en ajoutant un company_id
    """
    company_id = None
    if ((authUser["role"] == "USER") or (authUser["company_id"] == None and authUser["role"] != "MAINTAINER")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if (authUser["role"] == "MAINTAINER" and not planning.company_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    elif (authUser["role"] == "MAINTAINER"):
        company_id = planning.company_id
    else:
        company_id = authUser["company_id"]

    allPlannings = db.query(PlanningEntity).filter_by(
        company_id=planning.company_id).all()
    isExistingPlanning = False
    for db_planning in allPlannings:
        if (decrypt(db_planning.name) == planning.name):
            isExistingPlanning = True
            break
    if isExistingPlanning:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Planning with this name already exists")

    db_planning = PlanningEntity(
        name=encrypt(planning.name),
        company_id=company_id
    )

    db.add(db_planning)
    db.commit()
    db.refresh(db_planning)

    db_planning_decrypted = dict(
        id=db_planning.id,
        name=decrypt(db_planning.name),
        company_id=db_planning.company_id
    )

    return db_planning_decrypted


@router.delete("/planning/{planningId}")
async def delete_planning_by_id(planningId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Planning:
    """
    Supprimer un planning via son id
    Les MAINTAINER doivent remplir company_id
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    old_company = db.query(PlanningEntity).filter_by(id=planningId).first()
    db_company = db.query(PlanningEntity).filter_by(id=planningId).first()

    if db_company == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.delete(db_company)
    db.commit()

    return old_company.__dict__


@router.patch("/planning/{planningId}")
async def update_planning_by_id(planningId: int, planning: PlanningChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Planning:
    """
    Mettre à jour une entreprise via son id
    Rôle MAINTAINER requis
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_planning = db.query(PlanningEntity).filter_by(id=planningId).first()

    if db_planning == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    db_planning.name = encrypt(
        planning.name) if planning.name else db_planning.name
    db_planning.updated_at = datetime.now()
    db.commit()
    db.refresh(db_planning)

    db_company_decrypted = dict(
        id=db_planning.id,
        name=decrypt(db_planning.name),
        company_id=db_planning.company_id,
        created_at=db_planning.created_at,
        updated_at=db_planning.updated_at
    )

    return db_company_decrypted
