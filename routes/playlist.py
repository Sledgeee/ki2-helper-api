from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Playlist, PlaylistUpdate

router = APIRouter(tags=["playlist"], prefix="/playlists")


@router.post("/",
             response_description="Create a new playlist",
             status_code=status.HTTP_201_CREATED, response_model=Playlist)
async def create_playlist(request: Request, playlist: Playlist = Body(...)):
    playlist = jsonable_encoder(playlist)
    new_playlist = request.app.database["playlists"].insert_one(playlist)
    created_playlist = request.app.database["playlists"].find_one(
        {"_id": new_playlist.inserted_id}
    )

    return created_playlist


@router.get("/", response_description="List all playlists", response_model=List[Playlist])
async def list_playlists(request: Request):
    limit = request.query_params.get("limit") or 0
    skip = request.query_params.get("skip") or 0
    playlists = list(request.app.database["playlists"].find(limit=limit, skip=skip))
    return playlists


@router.get("/{_id}", response_description="Get a single playlists by id", response_model=Playlist)
async def find_playlist(_id: str, request: Request):
    if (playlist := request.app.database["playlists"].find_one({"_id": _id})) is not None:
        return playlist

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")


@router.patch("/{_id}", response_description="Update a playlist", response_model=Playlist)
async def update_playlist(_id: str, request: Request, playlist: PlaylistUpdate = Body(...)):
    playlist = {k: v for k, v in playlist.dict().items() if v is not None}

    if len(playlist) >= 1:
        update_result = request.app.database["playlists"].update_one(
            {"_id": _id}, {"$set": playlist}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")

    if (
        existing_playlist := request.app.database["playlists"].find_one({"_id": _id})
    ) is not None:
        return existing_playlist

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")


@router.delete("/{_id}", response_description="Delete a playlist")
async def delete_playlist(_id: str, request: Request, response: Response):
    delete_result = request.app.database["playlists"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist with ID {_id} not found")
