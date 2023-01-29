from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Week, WeekUpdate

router = APIRouter(tags=["week"], prefix="/week")


@router.post("/",
             response_description="Create a new week",
             status_code=status.HTTP_201_CREATED, response_model=Week)
async def create_week(request: Request, week: Week = Body(...)):
    week = jsonable_encoder(week)
    new_week = request.app.database["week"].insert_one(week)
    created_week = request.app.database["week"].find_one(
        {"_id": new_week.inserted_id}
    )

    return created_week


@router.get("/", response_description="List all weeks", response_model=List[Week])
async def list_weeks(request: Request):
    weeks = list(request.app.database["week"].find(limit=1))
    return weeks


@router.get("/{_id}", response_description="Get a single weeks by id", response_model=Week)
async def find_week(_id: str, request: Request):
    if (week := request.app.database["week"].find_one({"_id": _id})) is not None:
        return week

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Week with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a week", response_model=Week)
async def update_week(_id: str, request: Request, week: WeekUpdate = Body(...)):
    week = {k: v for k, v in week.dict().items() if v is not None}

    if len(week) >= 1:
        update_result = request.app.database["week"].update_one(
            {"_id": _id}, {"$set": week}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Week with ID {_id} not found")

    if (
        existing_week := request.app.database["week"].find_one({"_id": _id})
    ) is not None:
        return existing_week

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Week with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a week")
async def delete_week(_id: str, request: Request, response: Response):
    delete_result = request.app.database["week"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Week with ID {_id} not found")
