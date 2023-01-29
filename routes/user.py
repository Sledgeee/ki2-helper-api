from fastapi import APIRouter, Depends

from config import JWT_ACCESS_SECRET_KEY
from security import decode_jwt, get_token
from utils import get_photo

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/profile")
async def profile(token=Depends(get_token)):
    payload = decode_jwt(token, JWT_ACCESS_SECRET_KEY)
    pic = get_photo(int(payload["sub"]))
    return {
        "user_id": payload["sub"],
        "username": payload["username"],
        "first_name": payload["first_name"],
        "last_name": payload["last_name"],
        "pic": pic
    }
