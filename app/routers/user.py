# System Imports
from typing import Annotated
import datetime
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from entities import User as UserEntity
from models.user import User, UserChangeableFields
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt, hash_password

router = APIRouter()


@router.get("/users")
async def get_users(db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[User]:
    """
    Récupérer tout les utilisateurs
    """
    # Users with the role USER can't access this route
    if (authUser["role"] == "USER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    show_all = True if authUser["role"] != "MAINTAINER" else True
    
    db_users = db.query(UserEntity).all()
    db_users_dict = [user.__dict__ for user in db_users]

    admin_company_id = authUser["company_id"]
    # If the user is an ADMIN, we only return the users of his company
    if (authUser["role"] == "ADMIN"):
        if (authUser["company_id"] == None):
            return []
        db_users_dict = list(
            filter(lambda user: user["company_id"] == admin_company_id, db_users_dict))
        
    for user in db_users_dict:
        user["first_name"] = decrypt(user["first_name"])
        user["last_name"] = decrypt(user["last_name"])
        user["email"] = decrypt(user["email"]) if show_all else ""
        user["created_at"] = datetime.datetime.timestamp(user["created_at"]) if show_all else 0
        user["updated_at"] = datetime.datetime.timestamp(user["updated_at"]) if show_all else 0

    return db_users_dict


@router.get("/users/search")
async def get_user_by_id(id: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Récupérer un utilisateur par son id
    """
    # Users with the role USER and ADMIN can't access this route
    if (authUser and authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = db.query(UserEntity).filter_by(id=id).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    db_user_decrypted = dict(
        id=db_user.id,
        first_name=decrypt(db_user.first_name),
        last_name=decrypt(db_user.last_name),
        email=decrypt(db_user.email),
        role=db_user.role
    )

    return db_user_decrypted


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Créer un utilisateur
    Role: USER, ADMIN ou MAINTAINER
    """
    # Users with the role USER and ADMIN can't access this route
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    allUsers = db.query(UserEntity).all()
    isExistingCompany = False
    for db_user in allUsers:
        if (decrypt(db_user.email) == user.email):
            isExistingCompany = True
            break
    if isExistingCompany:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already exists")

    db_user = UserEntity(
        first_name=encrypt(user.first_name),
        last_name=encrypt(user.last_name),
        email=encrypt(user.email),
        password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_user_decrypted = dict(
        id=db_user.id,
        first_name=decrypt(db_user.first_name),
        last_name=decrypt(db_user.last_name),
        email=decrypt(db_user.email),
        role=db_user.role
    )

    return db_user_decrypted


@router.delete("/users/{userId}")
async def delete_user_by_id(userId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Supprimer un utilisateur par son id
    """
    # Users with the role USER and ADMIN can't access this route
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    old_user = db.query(UserEntity).filter_by(id=userId).first()
    db_user = db.query(UserEntity).filter_by(id=userId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.delete(db_user)
    db.commit()

    return old_user.__dict__


@router.patch("/users/{userId}")
async def update_user_by_id(userId: int, user: UserChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Mettre à jour un utilisateur par son id
    """
    # Users with the role USER and ADMIN can't patch other users
    if (userId != authUser["id"] and authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    db_user = db.query(UserEntity).filter_by(id=userId).first()

    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    db_user.first_name = encrypt(
        user.first_name) if user.first_name is not None else db_user.first_name
    db_user.last_name = encrypt(
        user.last_name) if user.last_name is not None else db_user.last_name
    db_user.email = encrypt(
        user.email) if user.email is not None else db_user.email
    db_user.password = hash_password(
        user.password) if user.password is not None else db_user.password
    db_user.role = user.role if user.role is not None else db_user.role
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
