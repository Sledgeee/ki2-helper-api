import db
from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Playlist, PlaylistUpdate

router = APIRouter(tags=["playlist"], prefix="/playlists")


@router.post("/",
             response_description="Create a new playlist",
             status_code=status.HTTP_201_CREATED, response_model=Playlist)
async def create_playlist(playlist: Playlist = Body(...)):
    playlist = jsonable_encoder(playlist)
    new_playlist = db.playlists.insert_one(playlist)
    created_playlist = db.playlists.find_one(
        {"_id": new_playlist.inserted_id}
    )

    return created_playlist


@router.get("/", response_description="List all playlists", response_model=List[Playlist])
async def list_playlists():
    playlists = list(db.playlists.find())
    return playlists


@router.get("/{_id}", response_description="Get a single playlists by id", response_model=Playlist)
async def find_playlist(_id: str):
    if (playlist := db.playlists.find_one({"_id": _id})) is not None:
        return playlist

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a playlist", response_model=Playlist)
async def update_playlist(_id: str, playlist: PlaylistUpdate = Body(...)):
    playlist = {k: v for k, v in playlist.dict().items() if v is not None}

    if len(playlist) >= 1:
        update_result = db.playlists.update_one(
            {"_id": _id}, {"$set": playlist}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")

    if (
        existing_playlist := db.playlists.find_one({"_id": _id})
    ) is not None:
        return existing_playlist

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a playlist")
async def delete_playlist(_id: str, response: Response):
    delete_result = db.lessons.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")
