from typing import Union
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt

import db
from config import JWT_ACCESS_SECRET_KEY, JWT_ALG

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JwtPayload(BaseModel):
    sub: str
    username: str


def create_access_token(payload: JwtPayload):
    to_encode = {
        "sub": payload.sub,
        "username": payload.username,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, JWT_ALG)
    return encoded_jwt


def decode_jwt(token: str, secret_key: str) -> Union[dict, None]:
    try:
        return jwt.decode(token, secret_key, JWT_ALG)
    except:
        return None


def raise_401(detail: str = "Not authenticated"):
    raise HTTPException(
        status_code=401,
        detail=detail,
        headers={"Authorization": "Bearer"}
    )


async def authorized(token: str = Depends(oauth2_scheme)):
    user = decode_jwt(token, JWT_ACCESS_SECRET_KEY)
    if not user:
        raise_401()
    admin = db.admins.find_one({"user_id": int(user["sub"])})
    if not admin:
        raise_401()
    return True


async def get_token(token: str = Depends(oauth2_scheme)):
    return token


async def is_super(token: str = Depends(oauth2_scheme)):
    user = decode_jwt(token, JWT_ACCESS_SECRET_KEY)
    if not user:
        raise_401()
    admin = db.admins.find_one({"user_id": int(user["sub"])})
    if not admin:
        raise_401()
    if admin["role"] != "super":
        raise_401("You have not access to this method")
    return True
