# System Imports
import hashlib
from typing import Annotated
from dependencies import get_db
# Libs Imports
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.user import User
from pydantic import BaseModel
from sqlalchemy.orm import Session
# Local Imports
from entities import User as UserEntity
from crypt import hash_password, encrypt, decrypt

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

JWT_KEY = "cW1nT8kIC7L8ZnijSHckA2c8f4TgN0DQcI6utcVgZJUdyFv0v0Bek8hxSKESeQV0zjMaK56x2CrzrMuyQBVB7lZ3NiSdvuxJTu18YD55nIBQLRIklzaiYT24iDGJihxvqnsZsmuwJaRFpygLBoRTaa5kVp9eQdmSBWwQ3SooRWTwsWaZDm9CVm3yb3P3X4IAlaAJwT4k"


async def decode_token(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        user = db.query(UserEntity).filter_by(
            id=decoded["id"]).first().__dict__
        user["first_name"] = decrypt(user["first_name"])
        user["last_name"] = decrypt(user["last_name"])
        user["email"] = decrypt(user["email"])
        if user == None:
            raise credentials_exception
    except JWTError:
        return credentials_exception
    return user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    hashed_password = hash_password(form_data.password)
    users = [user.__dict__ for user in db.query(UserEntity).all()]
    userFound = False
    
    for user in users:
        if decrypt(user["email"]) == form_data.username:
            userFound = user
            break

    if userFound != False:
        userFound = UserEntity(
            id=userFound["id"],
            password=userFound["password"]
        ).__dict__
        if hashed_password == userFound["password"]:
            data = dict()
            data["id"] = userFound["id"]
            return {
                "access_token": jwt.encode(data, JWT_KEY, algorithm="HS256"),
                "token_type": "bearer"
            }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Incorrect email or password")
