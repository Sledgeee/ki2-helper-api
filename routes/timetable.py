import db
from typing import List
from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from models import Timetable

router = APIRouter(tags=["timetable"], prefix="/timetable")


@router.post("/",
             response_description="Create a new timetable",
             status_code=status.HTTP_201_CREATED, response_model=Timetable)
async def create_timetable(timetable: Timetable = Body(...)):
    timetable = jsonable_encoder(timetable)
    new_timetable = db.timetable.insert_one(timetable)
    created_timetable = db.timetable.find_one(
        {"_id": new_timetable.inserted_id}
    )

    return created_timetable


@router.get("/", response_description="Get timetables", response_model=List[Timetable])
async def list_timetables():
    timetables = list(db.timetable.find())
    return timetables


@router.get("/{_id}", response_description="Get timetable by ID", response_model=Timetable)
async def find_timetable(_id: str):
    if (timetable := db.timetable.find_one({"_id": _id})) is not None:
        return timetable

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Timetable with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a timetable")
async def delete_timetable(_id: str, response: Response):
    delete_result = db.timetable.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Timetable with ID {_id} not found")
