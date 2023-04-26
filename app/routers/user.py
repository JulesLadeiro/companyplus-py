# System Imports
from typing import Annotated
# Libs Imports
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from models.user import User, UserChangeableFields
from entities import User as UserEntity
from dependencies import get_db
from internals.auth import decode_token
from crypt import encrypt, decrypt, hash_password

router = APIRouter()

users = []


@router.get("/users")
async def getUsers(db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[User]:
    """
    Récupérer tout les utilisateurs
    """
    if (authUser["role"] != "ADMIN" and authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_users = db.query(UserEntity).all()
    # for user in db_users set to dict and decrypt values
    db_users_dict = [user.__dict__ for user in db_users]
    for user in db_users_dict:
        user["first_name"] = decrypt(user["first_name"])
        user["last_name"] = decrypt(user["last_name"])
        user["email"] = decrypt(user["email"])
    # TODO if role is admin, send only users in its company
    return db_users_dict


@router.get("/users/search")
async def getUserById(id: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Récupérer un utilisateur par son id
    """
    if (authUser["role"] != "MAINTAINER"):
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
async def createUser(user: UserChangeableFields, db: Session = Depends(get_db)) -> User:
    """
    Créer un utilisateur
    Role: USER, ADMIN ou MAINTAINER
    """
    # if (authUser["role"] != "MAINTAINER"):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    isAlreadyRegistered = db.query(UserEntity).filter_by(
        email=encrypt(user.email)).first()
    if isAlreadyRegistered:
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
async def deleteUserById(userId: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Supprimer un utilisateur par son id
    """
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
async def updateUserById(userId: int, user: UserChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Mettre à jour un utilisateur par son id
    """
    oldUser = db.query(UserEntity).filter_by(id=userId).first()
    if oldUser == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    users.remove(oldUser[0])

    if user.name is not None:
        oldUser[0]["name"] = user.name
    if user.surname is not None:
        oldUser[0]["surname"] = user.surname
    if user.email is not None:
        oldUser[0]["email"] = user.email
    if user.password_hash is not None:
        oldUser[0]["password_hash"] = hash_password(user.password_hash)
    if user.tel is not None:
        oldUser[0]["tel"] = user.tel
    if user.newsletter is not None:
        oldUser[0]["newsletter"] = user.newsletter
    if user.is_client is not None:
        oldUser[0]["is_client"] = user.is_client

    users.append(oldUser[0].__dict__)
    return oldUser[0]
