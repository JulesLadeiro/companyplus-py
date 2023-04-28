# System Imports
from typing import Annotated
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from models.company import Company, CompanyChangeableFields
from entities import Company as CompanyEntity
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt

router = APIRouter()


@router.get("/company")
async def get_companies(db: Session = Depends(get_db), authUser: Annotated[Company, Depends(decode_token)] = None) -> list[Company]:
    """
    Récupérer toutes les entreprises
    """
    if (authUser["role"] == "ADMIN"):
        db_company = db.query(CompanyEntity).filter_by(
            id=authUser["company_id"]).first()
        if db_company == None:
            return []
        db_company_dict = db_company.__dict__
        db_company_dict["name"] = decrypt(db_company_dict["name"])
        db_company_dict["email"] = decrypt(db_company_dict["email"])
        db_company_dict["website"] = decrypt(
            db_company_dict["website"]) if db_company_dict["website"] else None
        db_company_dict["city"] = decrypt(db_company_dict["city"])
        db_company_dict["country"] = decrypt(db_company_dict["country"])
        return [db_company_dict]
    elif (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_company = db.query(CompanyEntity).all()

    db_company_dict = [company.__dict__ for company in db_company]
    for company in db_company_dict:
        company["name"] = decrypt(company["name"])
        company["email"] = decrypt(company["email"])
        company["website"] = decrypt(company["website"]) if company["website"] else None
        company["city"] = decrypt(company["city"])
        company["country"] = decrypt(company["country"])
        company["created_at"] = company["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        company["updated_at"] = company["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

    return db_company_dict


@router.post("/company", status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyChangeableFields, db: Session = Depends(get_db), authUser: Annotated[Company, Depends(decode_token)] = None) -> Company:
    """
    Créer une entreprise
    (Website optionnel)
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # TODO fix encryption
    isExistingCompany = db.query(CompanyEntity).filter_by(
        name=encrypt(company.name)).first()
    if isExistingCompany:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Company already exists")

    db_company = CompanyEntity(
        name=encrypt(company.name),
        email=encrypt(company.email),
        website=encrypt(company.website) if company.website else None,
        city=encrypt(company.city),
        country=encrypt(company.country)
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    db_company_decrypted = dict(
        id=db_company.id,
        name=decrypt(db_company.name),
        email=decrypt(db_company.email),
        website=decrypt(db_company.website) if db_company.website else None,
        city=decrypt(db_company.city),
        country=decrypt(db_company.country)
    )

    return db_company_decrypted

# TODO delete and patch company + add user to company / remove user from company
