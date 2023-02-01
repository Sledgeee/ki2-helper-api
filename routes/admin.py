import db
from fastapi import APIRouter, Depends, Response, status, HTTPException, Body
from config import JWT_ACCESS_SECRET_KEY
from models import BulkDelete
from security import decode_jwt, get_token, is_super
from utils import get_photo

router = APIRouter(tags=["admin"], prefix="/admins")


@router.get("/profile")
async def profile(token=Depends(get_token)):
    payload = decode_jwt(token, JWT_ACCESS_SECRET_KEY)
    pic = get_photo(int(payload["sub"]))
    return {
        "user_id": payload["sub"],
        "username": payload["username"],
        "pic": pic
    }


@router.get("/has-rights/{user_id}")
async def check_rights(user_id):
    if db.admins.find_one({"user_id": int(user_id)}, {"_id": 0, "username": 0}) is not None:
        return {"result": True}
    return {"result": False}


@router.delete("/{_id}", response_description="Delete manager")
async def delete_manager(_id: str, response: Response, auth=Depends(is_super)):
    delete_result = db.admins.delete_one({"_id": _id, "role": "manager"})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Manager with ID {_id} not found or it was super")


@router.post("/bulk-delete", response_description="Delete many managers")
async def delete_many_managers(response: Response, bulk_delete: BulkDelete = Body(...), auth=Depends(is_super)):
    delete_result = db.admins.delete_many({"_id": {
        "$in": bulk_delete.ids
    }, "role": "manager"})
    if delete_result.deleted_count >= 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Managers with specified IDs not found")
