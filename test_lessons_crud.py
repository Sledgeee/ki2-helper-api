from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.lesson import router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(router)
test_lesson = {
    "name": "Test Lesson",
    "short_name": "TL",
    "type": "пр.",
    "teacher": "Іванов І.І.",
    "zoom": "link"
}


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["MONGO_CONNECTION"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("lessons")


def test_create_lesson():
    with TestClient(app) as client:
        response = client.post("/lessons", json=test_lesson)
        assert response.status_code == 201

        body = response.json()
        assert body.get("name") == test_lesson.get("name")
        assert body.get("short_name") == test_lesson.get("short_name")
        assert body.get("type") == test_lesson.get("type")
        assert body.get("teacher") == test_lesson.get("teacher")
        assert body.get("zoom") == test_lesson.get("zoom")
        assert "_id" in body


def test_create_lesson_missing_name():
    with TestClient(app) as client:
        response = client.post("/lessons", json={
            "short_name": "TL",
            "type": "пр.",
            "teacher": "Іванов І.І.",
            "zoom": "link"
        })
        assert response.status_code == 422


def test_create_lesson_missing_short_name():
    with TestClient(app) as client:
        response = client.post("/lessons", json={
            "name": "Test Lesson",
            "type": "пр.",
            "teacher": "Іванов І.І.",
            "zoom": "link"
        })
        assert response.status_code == 422


def test_create_lesson_missing_type():
    with TestClient(app) as client:
        response = client.post("/lessons", json={
            "name": "Test Lesson",
            "short_name": "TL",
            "teacher": "Іванов І.І.",
            "zoom": "link"
        })
        assert response.status_code == 422


def test_create_lesson_missing_teacher():
    with TestClient(app) as client:
        response = client.post("/lessons", json={
            "name": "Test Lesson",
            "short_name": "TL",
            "type": "пр.",
            "zoom": "link"
        })
        assert response.status_code == 422


def test_create_lesson_missing_zoom():
    with TestClient(app) as client:
        response = client.post("/lessons", json={
            "name": "Test Lesson",
            "short_name": "TL",
            "type": "пр.",
            "teacher": "Іванов І.І."
        })
        assert response.status_code == 422


def test_get_lesson():
    with TestClient(app) as client:
        new_lesson = client.post("/lessons", json=test_lesson).json()
        get_lesson_response = client.get(f"/lessons/{new_lesson.get('_id')}")
        assert get_lesson_response.status_code == 200
        assert get_lesson_response.json() == new_lesson


def test_get_lesson_unexisting():
    with TestClient(app) as client:
        get_lesson_response = client.get("/lessons/unexisting_id")
        assert get_lesson_response.status_code == 404


def test_update_lesson():
    with TestClient(app) as client:
        new_lesson = client.post("/lessons", json=test_lesson).json()
        response = client.patch(f"/lessons/{new_lesson.get('_id')}", json={"zoom": "link2"})
        assert response.status_code == 200
        res_json = response.json()
        assert res_json.get("name") == test_lesson.get("name")
        assert res_json.get("zoom") == "link2"


def test_update_lesson_unexisting():
    with TestClient(app) as client:
        update_lesson_response = client.patch("/lessons/unexisting_id", json={"zoom": "link2"})
        assert update_lesson_response.status_code == 404


def test_delete_lesson():
    with TestClient(app) as client:
        new_lesson = client.post("/lessons", json=test_lesson).json()
        delete_lesson_response = client.delete(f"/lessons/{new_lesson.get('_id')}")
        assert delete_lesson_response.status_code == 204


def test_delete_lesson_unexisting():
    with TestClient(app) as client:
        delete_lesson_response = client.delete("/lessons/unexisting_id")
        assert delete_lesson_response.status_code == 404
