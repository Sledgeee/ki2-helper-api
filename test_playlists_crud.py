from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.playlist import router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["MONGO_CONNECTION"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("playlists")


def test_create_playlist():
    with TestClient(app) as client:
        response = client.post("/playlists", json={"link": "link"})
        assert response.status_code == 201

        body = response.json()
        assert body.get("link") == "link"
        assert "_id" in body


def test_create_playlist_missing_link():
    with TestClient(app) as client:
        response = client.post("/playlists", json={})
        assert response.status_code == 422


def test_get_playlist():
    with TestClient(app) as client:
        new_playlist = client.post("/playlists", json={"link": "link"}).json()
        get_playlist_response = client.get(f"/playlists/{new_playlist.get('_id')}")
        assert get_playlist_response.status_code == 200
        assert get_playlist_response.json() == new_playlist


def test_get_playlist_unexisting():
    with TestClient(app) as client:
        get_playlist_response = client.get("/playlists/unexisting_id")
        assert get_playlist_response.status_code == 404


def test_update_playlist():
    with TestClient(app) as client:
        new_playlist = client.post("/playlists", json={"link": "link"}).json()
        response = client.patch(f"/playlists/{new_playlist.get('_id')}", json={"link": "link2"})
        assert response.status_code == 200
        assert response.json().get("link") == "link2"


def test_update_playlist_unexisting():
    with TestClient(app) as client:
        update_playlist_response = client.patch("/playlists/unexisting_id", json={"link": "link2"})
        assert update_playlist_response.status_code == 404


def test_delete_playlist():
    with TestClient(app) as client:
        new_playlist = client.post("/playlists", json={"link": "link"}).json()
        delete_playlist_response = client.delete(f"/playlists/{new_playlist.get('_id')}")
        assert delete_playlist_response.status_code == 204


def test_delete_playlist_unexisting():
    with TestClient(app) as client:
        delete_playlist_response = client.delete("/playlists/unexisting_id")
        assert delete_playlist_response.status_code == 404
