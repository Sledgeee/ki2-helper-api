from typing import List

from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from models import Timetable

router = APIRouter(tags=["timetable"], prefix="/timetable")


@router.post("/",
             response_description="Create a new timetable",
             status_code=status.HTTP_201_CREATED, response_model=Timetable)
async def create_timetable(request: Request, timetable: Timetable = Body(...)):
    timetable = jsonable_encoder(timetable)
    new_timetable = request.app.database["timetable"].insert_one(timetable)
    created_timetable = request.app.database["timetable"].find_one(
        {"_id": new_timetable.inserted_id}
    )

    return created_timetable


@router.get("/", response_description="Get timetables", response_model=List[Timetable])
async def list_timetables(request: Request):
    limit = request.query_params.get("limit") or 0
    skip = request.query_params.get("skip") or 0
    timetables = list(request.app.database["timetable"].find(limit=limit, skip=skip))
    return timetables


@router.get("/{_id}", response_description="Get timetable by ID", response_model=Timetable)
async def find_timetable(_id: str, request: Request):
    if (timetable := request.app.database["timetable"].find_one({"_id": _id})) is not None:
        return timetable

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Timetable with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a timetable")
async def delete_timetable(_id: str, request: Request, response: Response):
    delete_result = request.app.database["timetable"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Timetable with ID {_id} not found")
