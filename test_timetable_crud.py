from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.timetable import router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(router)
items = [
    {
        "number": 1,
        "start_hour": 8,
        "start_minute": 0,
        "end_hour": 9,
        "end_minute": 20,
        "break": 15
    },
    {
        "number": 2,
        "start_hour": 9,
        "start_minute": 35,
        "end_hour": 10,
        "end_minute": 55,
        "break": 15
    }
]


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["MONGO_CONNECTION"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("timetable")


def test_create_timetable():
    with TestClient(app) as client:
        response = client.post("/timetable", json={
            "items": items
        })
        assert response.status_code == 201

        body = response.json()
        assert body.get("items") == items
        assert "_id" in body


def test_create_timetable_missing_items():
    with TestClient(app) as client:
        response = client.post("/timetable", json={})
        assert response.status_code == 422


def test_get_timetable():
    with TestClient(app) as client:
        new_timetable = client.post("/timetable", json={"items": items}).json()
        get_timetable_response = client.get(f"/timetable/{new_timetable.get('_id')}")
        assert get_timetable_response.status_code == 200
        assert get_timetable_response.json() == new_timetable


def test_get_timetable_unexisting():
    with TestClient(app) as client:
        get_timetable_response = client.get("/timetable/unexisting_id")
        assert get_timetable_response.status_code == 404


def test_delete_timetable():
    with TestClient(app) as client:
        new_timetable = client.post("/timetable", json={"items": items}).json()
        delete_timetable_response = client.delete(f"/timetable/{new_timetable.get('_id')}")
        assert delete_timetable_response.status_code == 204


def test_delete_timetable_unexisting():
    with TestClient(app) as client:
        delete_timetable_response = client.delete("/timetable/unexisting_id")
        assert delete_timetable_response.status_code == 404
