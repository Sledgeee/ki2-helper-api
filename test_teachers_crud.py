from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.teacher import router

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
    app.database.drop_collection("teachers")


def test_create_teacher():
    with TestClient(app) as client:
        response = client.post("/teachers", json={"name": "Іванов І.І."})
        assert response.status_code == 201

        body = response.json()
        assert body.get("name") == "Іванов І.І."
        assert "_id" in body


def test_create_teacher_missing_name():
    with TestClient(app) as client:
        response = client.post("/teachers", json={})
        assert response.status_code == 422


def test_get_teacher():
    with TestClient(app) as client:
        new_teachers = client.post("/teachers", json={"name": "Іванов І.І."}).json()
        get_teachers_response = client.get(f"/teachers/{new_teachers.get('_id')}")
        assert get_teachers_response.status_code == 200
        assert get_teachers_response.json() == new_teachers


def test_get_teacher_unexisting():
    with TestClient(app) as client:
        get_teachers_response = client.get("/teachers/unexisting_id")
        assert get_teachers_response.status_code == 404


def test_update_teacher():
    with TestClient(app) as client:
        new_teachers = client.post("/teachers", json={"name": "Іванов І.І."}).json()
        response = client.patch(f"/teachers/{new_teachers.get('_id')}", json={"name": "Зеленський В.О."})
        assert response.status_code == 200
        assert response.json().get("name") == "Зеленський В.О."


def test_update_teacher_unexisting():
    with TestClient(app) as client:
        update_teachers_response = client.patch("/teachers/unexisting_id", json={"name": "Зеленський В.О."})
        assert update_teachers_response.status_code == 404


def test_delete_teacher():
    with TestClient(app) as client:
        new_teachers = client.post("/teachers", json={"name": "Іванов І.І."}).json()
        delete_teachers_response = client.delete(f"/teachers/{new_teachers.get('_id')}")
        assert delete_teachers_response.status_code == 204


def test_delete_teacher_unexisting():
    with TestClient(app) as client:
        delete_teachers_response = client.delete("/teachers/unexisting_id")
        assert delete_teachers_response.status_code == 404
