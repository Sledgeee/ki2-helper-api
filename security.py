from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt

from config import JWT_ACCESS_SECRET_KEY, JWT_ALG, JWT_REFRESH_SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JwtPayload(BaseModel):
    sub: str
    username: str
    first_name: str
    last_name: str


def create_access_token(payload: JwtPayload):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": payload.sub,
        "username": payload.username,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "exp": exp
    }
    encoded_jwt = jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, JWT_ALG)
    return encoded_jwt


def create_refresh_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": sub,
        "exp": exp
    }
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, JWT_ALG)
    return encoded_jwt


def decode_jwt(token: str, secret_key: str) -> Union[dict, None]:
    try:
        return jwt.decode(token, secret_key, JWT_ALG)
    except:
        return None


async def authorized(token: str = Depends(oauth2_scheme)):
    user = decode_jwt(token, JWT_ACCESS_SECRET_KEY)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"Authorization": "Bearer"}
        )
    return True


async def get_token(token: str = Depends(oauth2_scheme)):
    return token
