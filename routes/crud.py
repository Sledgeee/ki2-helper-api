import db
import models
from fastapi import APIRouter, Body, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from typing import List, Union, Literal
from security import authorized

router = APIRouter(tags=["crud"], prefix="/crud")

Crud = Union[
    models.Birthday,
    models.Lesson,
    models.Playlist,
    models.Schedule,
    models.Teacher,
    models.Week
]

CrudUpdate = Union[
    models.BirthdayUpdate,
    models.LessonUpdate,
    models.PlaylistUpdate,
    models.ScheduleUpdate,
    models.TeacherUpdate,
    models.WeekUpdate
]

Collection = Literal[
    "birthdays",
    "lessons",
    "playlists",
    "schedule",
    "teachers",
    "week"
]


@router.post("/{collection}/",
             response_description="Create a new item",
             status_code=status.HTTP_201_CREATED, response_model=Crud)
async def create_item(collection: Collection, item: Crud = Body(...), auth=Depends(authorized)):
    item = jsonable_encoder(item)
    new_item = db.db[collection].insert_one(item)
    created_item = db.db[collection].find_one(
        {"_id": new_item.inserted_id}
    )
    return created_item


@router.get("/{collection}/", response_description="List all items", response_model=List[Union[Crud, models.Admin]])
async def list_items(collection: Union[Collection, Literal["admins", "timetable"]]):
    items = list(db.db[collection].find())
    return items


@router.get("/{collection}/{_id}/", response_description="Get a single item by id", response_model=Crud)
async def find_item(collection: Collection, _id: str):
    if (item := db.db[collection].find_one({"_id": _id})) is not None:
        return item

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {_id} not found")


@router.patch("/{collection}/{_id}/", response_description="Update an item", response_model=Crud)
async def update_item(collection: Collection, _id: str, update: CrudUpdate = Body(...), auth=Depends(authorized)):
    update = {k: v for k, v in update.dict().items() if v is not None}

    if len(update) >= 1:
        update_result = db.db[collection].update_one(
            {"_id": _id}, {"$set": update}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {_id} not found")

    if (existing_item := db.db[collection].find_one({"_id": _id})) is not None:
        return existing_item

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {_id} not found")


@router.delete("/{collection}/{_id}/", response_description="Delete an item")
async def delete_item(collection: Collection, _id: str, response: Response, auth=Depends(authorized)):
    delete_result = db.db[collection].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {_id} not found")


@router.post("/{collection}/bulk-delete/", response_description="Delete many items")
async def delete_many_items(collection: Collection, response: Response, bulk: models.BulkDelete = Body(...),
                            auth=Depends(authorized)):
    delete_result = db.db[collection].delete_many({"_id": {
        "$in": bulk.ids
    }})
    if delete_result.deleted_count >= 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Items with specified IDs not found")
