import db
from fastapi import APIRouter, Body, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from typing import Union, Literal, List
from security import authorized
from models import EitherModel, BulkDelete, Admin, Timetable

router = APIRouter(tags=["crud"], prefix="/crud")

Collection = Literal[
    "birthdays",
    "lessons",
    "playlists",
    "schedule",
    "teachers",
    "week",
    "cron"
]

ExtendedCollection = Union[Collection, Literal["admins", "timetable"]]
ExtendedEitherModel = Union[EitherModel, Admin, Timetable]


@router.post("/{collection}/",
             response_description="Create a new item", response_model=EitherModel,
             status_code=status.HTTP_201_CREATED)
async def create_item(collection: Collection, item: EitherModel = Body(...), auth=Depends(authorized)):
    item = jsonable_encoder(item)
    new_item = db.db[collection].insert_one(item)
    created_item = db.db[collection].find_one(
        {"_id": new_item.inserted_id}
    )
    return created_item


@router.get("/{collection}/", response_description="List all items", response_model=List[ExtendedEitherModel])
async def list_items(collection: ExtendedCollection):
    items = list(db.db[collection].find())
    return items


@router.get("/{collection}/{_id}/", response_description="Get a single item by id", response_model=ExtendedEitherModel)
async def find_item(collection: ExtendedCollection, _id: str):
    if (item := db.db[collection].find_one({"_id": _id})) is not None:
        return item

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {_id} not found")


@router.put("/{collection}/{_id}/", response_description="Update an item")
async def update_item(collection: Collection, _id: str, update=Body(...), auth=Depends(authorized)):
    update_result = db.db[collection].update_one(
        {"_id": _id}, {"$set": jsonable_encoder(update)}
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
async def delete_many_items(collection: Collection, response: Response, bulk: BulkDelete = Body(...),
                            auth=Depends(authorized)):
    delete_result = db.db[collection].delete_many({"_id": {
        "$in": bulk.ids
    }})
    if delete_result.deleted_count >= 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Items with specified IDs not found")
