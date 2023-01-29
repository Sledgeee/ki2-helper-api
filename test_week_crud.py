from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.week import router

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
    app.database.drop_collection("week")


def test_create_week():
    with TestClient(app) as client:
        response = client.post("/week", json={"type": "Чисельник"})
        assert response.status_code == 201

        body = response.json()
        assert body.get("type") == "Чисельник"
        assert "_id" in body


def test_create_week_missing_type():
    with TestClient(app) as client:
        response = client.post("/week", json={})
        assert response.status_code == 422


def test_get_week():
    with TestClient(app) as client:
        new_week = client.post("/week", json={"type": "Чисельник"}).json()
        get_week_response = client.get(f"/week/{new_week.get('_id')}")
        assert get_week_response.status_code == 200
        assert get_week_response.json() == new_week


def test_get_week_unexisting():
    with TestClient(app) as client:
        get_week_response = client.get("/week/unexisting_id")
        assert get_week_response.status_code == 404


def test_update_week():
    with TestClient(app) as client:
        new_week = client.post("/week", json={"type": "Чисельник"}).json()
        response = client.patch(f"/week/{new_week.get('_id')}", json={"type": "Знаменник"})
        assert response.status_code == 200
        assert response.json().get("type") == "Знаменник"


def test_update_week_unexisting():
    with TestClient(app) as client:
        update_week_response = client.patch("/week/unexisting_id", json={"type": "Знаменник"})
        assert update_week_response.status_code == 404


def test_delete_week():
    with TestClient(app) as client:
        new_week = client.post("/week", json={"type": "Чисельник"}).json()
        delete_week_response = client.delete(f"/week/{new_week.get('_id')}")
        assert delete_week_response.status_code == 204


def test_delete_week_unexisting():
    with TestClient(app) as client:
        delete_week_response = client.delete("/week/unexisting_id")
        assert delete_week_response.status_code == 404
