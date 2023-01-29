from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Lesson, LessonUpdate

router = APIRouter(tags=["lesson"], prefix="/lessons")


@router.post("/",
             response_description="Create a new lesson",
             status_code=status.HTTP_201_CREATED, response_model=Lesson)
async def create_lesson(request: Request, lesson: Lesson = Body(...)):
    lesson = jsonable_encoder(lesson)
    new_lesson = request.app.database["lessons"].insert_one(lesson)
    created_lesson = request.app.database["lessons"].find_one(
        {"_id": new_lesson.inserted_id}
    )

    return created_lesson


@router.get("/", response_description="List all lessons", response_model=List[Lesson])
async def list_lessons(request: Request):
    limit = request.query_params.get("limit") or 0
    skip = request.query_params.get("skip") or 0
    lessons = list(request.app.database["lessons"].find(limit=limit, skip=skip))
    return lessons


@router.get("/{_id}", response_description="Get a single lesson by id", response_model=Lesson)
async def find_lesson(_id: str, request: Request):
    if (lesson := request.app.database["lessons"].find_one({"_id": _id})) is not None:
        return lesson

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a lesson", response_model=Lesson)
async def update_lesson(_id: str, request: Request, lesson: LessonUpdate = Body(...)):
    lesson = {k: v for k, v in lesson.dict().items() if v is not None}

    if len(lesson) >= 1:
        update_result = request.app.database["lessons"].update_one(
            {"_id": _id}, {"$set": lesson}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson with ID {_id} not found")

    if (
        existing_lesson := request.app.database["lessons"].find_one({"_id": _id})
    ) is not None:
        return existing_lesson

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a lesson")
def delete_lesson(_id: str, request: Request, response: Response):
    delete_result = request.app.database["lessons"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson with ID {_id} not found")
