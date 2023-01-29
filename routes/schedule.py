import db
from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Schedule, ScheduleUpdate

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.post("/",
             response_description="Create a new schedule",
             status_code=status.HTTP_201_CREATED, response_model=Schedule)
async def create_schedule(schedule: Schedule = Body(...)):
    schedule = jsonable_encoder(schedule)
    new_schedule = db.schedule.insert_one(schedule)
    created_schedule = db.schedule.find_one(
        {"_id": new_schedule.inserted_id}
    )

    return created_schedule


@router.get("/", response_description="List schedule", response_model=List[Schedule])
async def list_schedule():
    schedules = list(db.schedule.find())
    return schedules


@router.get("/{_id}", response_description="Get a single schedule by id", response_model=Schedule)
async def find_schedule(_id: str):
    if (schedule := db.schedule.find_one({"_id": _id})) is not None:
        return schedule

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a schedule", response_model=Schedule)
async def update_schedule(_id: str, schedule: ScheduleUpdate = Body(...)):
    schedule = {k: v for k, v in schedule.dict().items() if v is not None}

    if len(schedule) >= 1:
        update_result = db.schedule.update_one(
            {"_id": _id}, {"$set": schedule}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule with ID {_id} not found")

    if (
        existing_schedule := db.schedule.find_one({"_id": _id})
    ) is not None:
        return existing_schedule

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a schedule")
async def delete_schedule(_id: str, response: Response):
    delete_result = db.schedule.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule with ID {_id} not found")
