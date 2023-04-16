# Libs Imports
import hashlib
from fastapi import APIRouter, status, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
# Local Imports
from models.user import User, UserOptionnalFields
from entities import User as UserEntity
from dependencies import get_db

router = APIRouter()

users = []


def hash_password(password: str):
    return hashlib.sha256(f'{password}'.encode('utf-8')).hexdigest()


@router.get("/users")
def getUser(db: Session = Depends(get_db)) -> list[User]:
    """
    Récupérer tout les utilisateurs
    """
    db_users = db.query(UserEntity).all()
    db_users_dict = [user.__dict__ for user in db_users]
    return db_users_dict


@router.get("/users/search")
async def getUserByUserName(userName: str):
    """
    Récupérer un utilisateur par son nom
    """
    return list(filter(lambda x: x["name"] == userName, users))


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def createUser(user: User) -> User:
    """
    Créer un utilisateur
    """
    if user.email.lower() in [(user["email"]).lower() for user in users]:
        raise HTTPException(status_code=400, detail="Email already used")
    user.id = users[-1]["id"] + 1
    user.password_hash = hash_password(user.password_hash)
    users.append(user.__dict__)
    return user


@router.delete("/users/{userId}")
async def deleteUserById(userId: int) -> User:
    """
    Supprimer un utilisateur par son id
    """
    oldUser = list(filter(lambda x: x["id"] == userId, users))
    users.remove(oldUser[0])
    return oldUser[0]


@router.put("/users/{userId}")
async def updateUserById(userId: int, user: User) -> User:
    """
    Mettre à jour un utilisateur par son id
    """
    oldUser = list(filter(lambda x: x["id"] == userId, users))
    users.remove(oldUser[0])
    users.append(user.__dict__)
    return user


@router.patch("/users/{userId}")
async def updateUserById(userId: int, user: UserOptionnalFields) -> User:
    """
    Mettre à jour un utilisateur par son id
    """
    oldUser = list(filter(lambda x: x["id"] == userId, users))

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
