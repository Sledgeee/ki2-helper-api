from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Teacher, TeacherUpdate

router = APIRouter(tags=["teacher"], prefix="/teachers")


@router.post("/",
             response_description="Create a new teacher",
             status_code=status.HTTP_201_CREATED, response_model=Teacher)
async def create_teacher(request: Request, teacher: Teacher = Body(...)):
    teacher = jsonable_encoder(teacher)
    new_teacher = request.app.database["teachers"].insert_one(teacher)
    created_teacher = request.app.database["teachers"].find_one(
        {"_id": new_teacher.inserted_id}
    )

    return created_teacher


@router.get("/", response_description="List all teachers", response_model=List[Teacher])
async def list_teachers(request: Request):
    limit = request.query_params.get("limit") or 0
    skip = request.query_params.get("skip") or 0
    teachers = list(request.app.database["teachers"].find(limit=limit, skip=skip))
    return teachers


@router.get("/{_id}", response_description="Get a single teachers by id", response_model=Teacher)
async def find_teacher(_id: str, request: Request):
    if (teacher := request.app.database["teachers"].find_one({"_id": _id})) is not None:
        return teacher

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a teacher", response_model=Teacher)
async def update_teacher(_id: str, request: Request, teacher: TeacherUpdate = Body(...)):
    teacher = {k: v for k, v in teacher.dict().items() if v is not None}

    if len(teacher) >= 1:
        update_result = request.app.database["teachers"].update_one(
            {"_id": _id}, {"$set": teacher}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")

    if (
        existing_teacher := request.app.database["teachers"].find_one({"_id": _id})
    ) is not None:
        return existing_teacher

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a teacher")
async def delete_teacher(_id: str, request: Request, response: Response):
    delete_result = request.app.database["teachers"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")
