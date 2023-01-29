from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Birthday, BirthdayUpdate, BulkDelete

router = APIRouter(tags=["birthday"], prefix="/birthdays")


@router.post("/",
             response_description="Create a new birthday",
             status_code=status.HTTP_201_CREATED, response_model=Birthday)
async def create_birthday(request: Request, birthday: Birthday = Body(...)):
    birthday = jsonable_encoder(birthday)
    new_birthday = request.app.database["birthdays"].insert_one(birthday)
    created_birthday = request.app.database["birthdays"].find_one(
        {"_id": new_birthday.inserted_id}
    )

    return created_birthday


@router.get("/", response_description="List all birthdays", response_model=List[Birthday])
async def list_birthdays(request: Request):
    limit = request.query_params.get("limit") or 0
    skip = request.query_params.get("skip") or 0
    birthdays = list(request.app.database["birthdays"].find(limit=limit, skip=skip))
    return birthdays


@router.get("/{_id}", response_description="Get a single birthdays by id", response_model=Birthday)
async def find_birthday(_id: str, request: Request):
    if (birthday := request.app.database["birthdays"].find_one({"_id": _id})) is not None:
        return birthday

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Birthday with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a birthday", response_model=Birthday)
async def update_birthday(_id: str, request: Request, birthday: BirthdayUpdate = Body(...)):
    birthday = {k: v for k, v in birthday.dict().items() if v is not None}

    if len(birthday) >= 1:
        update_result = request.app.database["birthdays"].update_one(
            {"_id": _id}, {"$set": birthday}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Birthday with ID {_id} not found")

    if (
        existing_birthday := request.app.database["birthdays"].find_one({"_id": _id})
    ) is not None:
        return existing_birthday

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Birthday with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a birthday")
async def delete_birthday(_id: str, request: Request, response: Response):
    delete_result = request.app.database["birthdays"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Birthday with ID {_id} not found")


@router.post("/bulk", response_description="Delete many birthdays")
async def delete_many_birthdays(request: Request, response: Response, bulk_delete: BulkDelete = Body(...)):
    delete_result = request.app.database["birthdays"].delete_many({"_id": {
        "$in": bulk_delete.ids
    }})
    if delete_result.deleted_count >= 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Birthdays with specified IDs not found")
