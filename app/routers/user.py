# System Imports
from typing import Annotated
# Libs Imports
import hashlib
from fastapi import APIRouter, status, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from models.user import User, UserChangeableFields
from entities import User as UserEntity
from dependencies import get_db
from internals.auth import decode_token

router = APIRouter()

users = []


def hash_password(password: str):
    return hashlib.sha256(f'{password}'.encode('utf-8')).hexdigest()


@router.get("/users")
async def getUsers(db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[User]:
    """
    Récupérer tout les utilisateurs
    """
    if (authUser["role"] != "ADMIN" and authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_users = db.query(UserEntity).all()
    db_users_dict = [user.__dict__ for user in db_users]
    # TODO if role is admin, send only users in its company
    return db_users_dict


@router.get("/users/search")
async def getUserByUserName(id: int, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> list[User]:
    """
    Récupérer un utilisateur par son id
    """
    if (authUser["role"] != "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_user = db.query(UserEntity).filter_by(id=id).first()
    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    # TODO if role is admin, send only users in its company
    return db_user.__dict__


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def createUser(user: UserChangeableFields, db: Session = Depends(get_db), authUser: Annotated[User, Depends(decode_token)] = None) -> User:
    """
    Créer un utilisateur
    Role: USER, ADMIN ou MAINTAINER
    """
    if (authUser["role"] != "MAINTAINER"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_user = UserEntity(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.__dict__


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


# @router.put("/users/{userId}")
# async def updateUserById(userId: int, user: User) -> User:
#     """
#     Mettre à jour un utilisateur par son id
#     """
#     oldUser = list(filter(lambda x: x["id"] == userId, users))
#     users.remove(oldUser[0])
#     users.append(user.__dict__)
#     return user


# @router.patch("/users/{userId}")
# async def updateUserById(userId: int, user: UserChangeableFields) -> User:
#     """
#     Mettre à jour un utilisateur par son id
#     """
#     oldUser = list(filter(lambda x: x["id"] == userId, users))

#     users.remove(oldUser[0])

#     if user.name is not None:
#         oldUser[0]["name"] = user.name
#     if user.surname is not None:
#         oldUser[0]["surname"] = user.surname
#     if user.email is not None:
#         oldUser[0]["email"] = user.email
#     if user.password_hash is not None:
#         oldUser[0]["password_hash"] = hash_password(user.password_hash)
#     if user.tel is not None:
#         oldUser[0]["tel"] = user.tel
#     if user.newsletter is not None:
#         oldUser[0]["newsletter"] = user.newsletter
#     if user.is_client is not None:
#         oldUser[0]["is_client"] = user.is_client

#     users.append(oldUser[0].__dict__)
#     return oldUser[0]
