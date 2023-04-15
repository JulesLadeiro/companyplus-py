# System Imports
from typing import Annotated
# Libs Imports
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from templates.user import User
import hashlib
# Local Imports
from routers.user import users

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

JWT_KEY = "cW1nT8kIC7L8ZnijSHckA2c8f4TgN0DQcI6utcVgZJUdyFv0v0Bek8hxSKESeQV0zjMaK56x2CrzrMuyQBVB7lZ3NiSdvuxJTu18YD55nIBQLRIklzaiYT24iDGJihxvqnsZsmuwJaRFpygLBoRTaa5kVp9eQdmSBWwQ3SooRWTwsWaZDm9CVm3yb3P3X4IAlaAJwT4k"


def hash_password(password: str):
    return hashlib.sha256(f'{password}'.encode('utf-8')).hexdigest()


async def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    except JWTError:
        return credentials_exception
    return decoded


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed_password = hash_password(form_data.password)
    for user in users:
        if user["name"].lower() == form_data.username.lower():
            if hashed_password == user["password_hash"]:
                data = dict()
                data["id"] = user["id"]
                data["name"] = user["name"]
                return {
                    "access_token": jwt.encode(data, JWT_KEY, algorithm="HS256"),
                    "token_type": "bearer"
                }
            break
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Incorrect username or password")


@router.get("/items/")
async def read_items(user: Annotated[User, Depends(decode_token)]):
    return {"user": user}
