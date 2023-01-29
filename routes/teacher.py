import db
from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Teacher, TeacherUpdate

router = APIRouter(tags=["teacher"], prefix="/teachers")


@router.post("/",
             response_description="Create a new teacher",
             status_code=status.HTTP_201_CREATED, response_model=Teacher)
async def create_teacher(teacher: Teacher = Body(...)):
    teacher = jsonable_encoder(teacher)
    new_teacher = db.teachers.insert_one(teacher)
    created_teacher = db.teachers.find_one(
        {"_id": new_teacher.inserted_id}
    )

    return created_teacher


@router.get("/", response_description="List all teachers", response_model=List[Teacher])
async def list_teachers():
    teachers = list(db.teachers.find())
    return teachers


@router.get("/{_id}", response_description="Get a single teachers by id", response_model=Teacher)
async def find_teacher(_id: str):
    if (teacher := db.teachers.find_one({"_id": _id})) is not None:
        return teacher

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a teacher", response_model=Teacher)
async def update_teacher(_id: str, teacher: TeacherUpdate = Body(...)):
    teacher = {k: v for k, v in teacher.dict().items() if v is not None}

    if len(teacher) >= 1:
        update_result = db.teachers.update_one(
            {"_id": _id}, {"$set": teacher}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")

    if (
        existing_teacher := db.teachers.find_one({"_id": _id})
    ) is not None:
        return existing_teacher

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a teacher")
async def delete_teacher(_id: str, response: Response):
    delete_result = db.teachers.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {_id} not found")
