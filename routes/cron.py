from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from models import Cron, CronUpdate

router = APIRouter(tags=["cron"], prefix="/cron")


@router.post("/",
             response_description="Create a new cron",
             status_code=status.HTTP_201_CREATED, response_model=Cron)
async def create_cron(request: Request, cron: Cron = Body(...)):
    cron = jsonable_encoder(cron)
    new_cron = request.app.database["cron"].insert_one(cron)
    created_cron = request.app.database["cron"].find_one(
        {"_id": new_cron.inserted_id}
    )

    return created_cron


@router.get("/{_id}", response_description="Get cron config", response_model=Cron)
async def find_cron(_id: str, request: Request):
    if (cron := request.app.database["cron"].find_one({"_id": _id})) is not None:
        return cron

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cron with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a cron", response_model=Cron)
async def update_cron(_id: str, request: Request, cron: CronUpdate = Body(...)):
    cron = {k: v for k, v in cron.dict().items() if v is not None}

    if len(cron) >= 1:
        update_result = request.app.database["cron"].update_one(
            {"_id": _id}, {"$set": cron}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cron with ID {_id} not found")

    if (
        existing_cron := request.app.database["cron"].find_one({"_id": _id})
    ) is not None:
        return existing_cron

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cron with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a cron")
async def delete_cron(_id: str, request: Request, response: Response):
    delete_result = request.app.database["cron"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cron with ID {_id} not found")
