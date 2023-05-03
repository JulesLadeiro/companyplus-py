# System Imports
from typing import Annotated
import datetime
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session, contains_eager
from fastapi import Depends
# Local Imports
from models.company import Company, CompanyChangeableFields
from models.user import User
from entities import Company as CompanyEntity, User as UserEntity
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt

router = APIRouter()


@router.get("/company")
async def get_companies(db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[Company]:
    """
    Récupérer toutes les entreprises
    """
    if (authUser["role"] == "ADMIN"):
        db_company = db.query(CompanyEntity).filter_by(id=authUser["company_id"]).join(UserEntity).options(contains_eager(
            CompanyEntity.users)).first()
        if db_company == None:
            return []
        company_dict = db_company.__dict__
        print(company_dict)
        company_dict["name"] = decrypt(company_dict["name"])
        company_dict["website"] = decrypt(
            company_dict["website"]) if company_dict["website"] else None
        company_dict["city"] = decrypt(
            company_dict["city"]) if company_dict["city"] else None
        company_dict["country"] = decrypt(
            company_dict["country"]) if company_dict["country"] else None
        company_dict["created_at"] = None
        company_dict["updated_at"] = None
        user_list = company_dict["users"]
        company_dict["users"] = []
        for user in user_list:
            user_dict = user.__dict__
            user_dict["id"] = user_dict["id"]
            user_dict["first_name"] = decrypt(user_dict["first_name"])
            user_dict["last_name"] = decrypt(user_dict["last_name"])
            user_dict["email"] = None
            user_dict["password"] = None
            user_dict["role"] = user_dict["role"]
            user_dict["company_id"] = user_dict["company_id"]
            user_dict["created_at"] = None
            user_dict["updated_at"] = None
            company_dict["users"].append(user_dict)
        return [company_dict]
    elif (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_company = db.query(CompanyEntity).join(UserEntity).options(
        contains_eager(CompanyEntity.users)).all()

    db_company_dict = []
    for company in db_company:
        company_dict = company.__dict__
        company_dict["name"] = decrypt(company_dict["name"])
        company_dict["website"] = decrypt(
            company_dict["website"]) if company_dict["website"] else None
        company_dict["city"] = decrypt(
            company_dict["city"]) if company_dict["city"] else None
        company_dict["country"] = decrypt(
            company_dict["country"]) if company_dict["country"] else None
        company_dict["created_at"] = company_dict["created_at"].strftime(
            "%Y-%m-%d %H:%M:%S")
        company_dict["updated_at"] = company_dict["updated_at"].strftime(
            "%Y-%m-%d %H:%M:%S")
        user_list = company_dict["users"]
        company_dict["users"] = []
        for user in user_list:
            user_dict = user.__dict__
            user_dict["id"] = user_dict["id"]
            user_dict["first_name"] = decrypt(user_dict["first_name"])
            user_dict["last_name"] = decrypt(user_dict["last_name"])
            user_dict["email"] = decrypt(user_dict["email"])
            user_dict["password"] = None
            user_dict["role"] = user_dict["role"]
            user_dict["company_id"] = user_dict["company_id"]
            user_dict["created_at"] = user_dict["created_at"].strftime(
                "%Y-%m-%d %H:%M:%S")
            user_dict["updated_at"] = user_dict["updated_at"].strftime(
                "%Y-%m-%d %H:%M:%S")
            company_dict["users"].append(user_dict)
        db_company_dict.append(company_dict)

    return db_company_dict


@router.post("/company", status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Company:
    """
    Créer une entreprise
    (Website optionnel)
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    allCompanies = db.query(CompanyEntity).all()
    isExistingCompany = False
    for db_company in allCompanies:
        if (decrypt(db_company.name) == company.name):
            isExistingCompany = True
            break
    if isExistingCompany:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Company already exists")

    db_company = CompanyEntity(
        name=encrypt(company.name),
        website=encrypt(company.website) if company.website else None,
        city=encrypt(company.city) if company.city else None,
        country=encrypt(company.country) if company.country else None,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    db_company_decrypted = dict(
        id=db_company.id,
        name=decrypt(db_company.name),
        website=decrypt(db_company.website) if db_company.website else None,
        city=decrypt(db_company.city) if db_company.city else None,
        country=decrypt(db_company.country) if db_company.country else None,
    )

    return db_company_decrypted


@router.delete("/company/{companyId}")
async def delete_company_by_id(companyId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Company:
    """
    Supprimer un utilisateur par son id
    Rôle MAINTAINER requis
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    old_company = db.query(CompanyEntity).filter_by(id=companyId).first()
    db_company = db.query(CompanyEntity).filter_by(id=companyId).first()

    if db_company == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.delete(db_company)
    db.commit()

    return old_company.__dict__


@router.patch("/company/{companyId}")
async def update_company_by_id(companyId: int, company: CompanyChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Company:
    """
    Mettre à jour une entreprise via son id
    Rôle MAINTAINER requis
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_company = db.query(CompanyEntity).filter_by(id=companyId).first()

    if db_company == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    db_company.name = encrypt(
        company.name) if company.name else db_company.name
    db_company.website = encrypt(
        company.website) if company.website else db_company.website
    db_company.city = encrypt(
        company.city) if company.city else db_company.city
    db_company.country = encrypt(
        company.country) if company.country else db_company.country
    db_company.updated_at = datetime.now()
    db.commit()
    db.refresh(db_company)

    db_company_decrypted = dict(
        id=db_company.id,
        name=decrypt(db_company.name),
        website=decrypt(db_company.website) if db_company.website else None,
        city=decrypt(db_company.city) if db_company.city else None,
        country=decrypt(db_company.country) if db_company.country else None,
        created_at=db_company.created_at,
        updated_at=db_company.updated_at
    )

    return db_company_decrypted


@router.post("/company-add-user/{userId}")
async def add_user_to_company(userId: int, companyId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Company:
    """
    Ajouter un utilisateur à une entreprise
    Rôle MAINTAINER requis
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = db.query(UserEntity).filter_by(id=userId).first()
    db_company = db.query(CompanyEntity).filter_by(id=companyId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    elif db_company == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Company not found")
    elif db_user.company_id == companyId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already in this company")
    elif db_user.company_id != None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already has a company")
    elif db_user.role == "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Maintainer user cannot be added to a company")

    db_user.company_id = companyId
    db.commit()
    db.refresh(db_user)

    return db_user.__dict__


@router.delete("/company-remove-user/{userId}")
async def remove_user_from_company(userId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> Company:
    """
    Supprimer un utilisateur d'une entreprise
    Rôle MAINTAINER requis
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = db.query(UserEntity).filter_by(id=userId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    elif db_user.company_id == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User does not have a company")
    elif db_user.role == "MAINTAINER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Maintainer user cannot be removed from a company")

    db_user.company_id = None
    db.commit()
    db.refresh(db_user)

    return db_user.__dict__
