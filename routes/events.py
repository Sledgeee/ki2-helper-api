import db
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, status, Response, HTTPException
from models import ScheduledEvent

router = APIRouter(tags=["events"], prefix="/events")


@router.get("/", response_description="List events")
async def events_all():
    events = list(db.events.find())
    return events


@router.post("/", response_description="Add event", status_code=status.HTTP_201_CREATED)
async def new_event(item: ScheduledEvent = Body(...)):
    item = jsonable_encoder(item)
    new_item = db.events.insert_one(item)
    created_item = db.events.find_one(
        {"_id": new_item.inserted_id}
    )
    return created_item


@router.delete("/{_id}", response_description="Delete event", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(_id: str, response: Response):
    delete_result = db.events.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {_id} not found")
