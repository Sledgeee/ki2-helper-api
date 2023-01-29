from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.birthday import router

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
    app.database.drop_collection("birthdays")


def test_create_birthday():
    with TestClient(app) as client:
        response = client.post("/birthdays", json={"date": "31.12", "student_name": "Іванов Іван"})
        assert response.status_code == 201

        body = response.json()
        assert body.get("date") == "31.12"
        assert body.get("student_name") == "Іванов Іван"
        assert "_id" in body


def test_create_birthday_missing_date():
    with TestClient(app) as client:
        response = client.post("/birthdays", json={"student_name": "Іванов Іван"})
        assert response.status_code == 422


def test_create_birthday_missing_student_name():
    with TestClient(app) as client:
        response = client.post("/birthdays", json={"date": "31.12"})
        assert response.status_code == 422


def test_get_birthday():
    with TestClient(app) as client:
        new_birthday = client.post("/birthdays", json={"date": "31.12", "student_name": "Іванов Іван"}).json()
        get_birthday_response = client.get(f"/birthdays/{new_birthday.get('_id')}")
        assert get_birthday_response.status_code == 200
        assert get_birthday_response.json() == new_birthday


def test_get_birthday_unexisting():
    with TestClient(app) as client:
        get_birthday_response = client.get("/birthdays/unexisting_id")
        assert get_birthday_response.status_code == 404


def test_update_birthday():
    with TestClient(app) as client:
        new_birthday = client.post("/birthdays", json={"date": "31.12", "student_name": "Іванов Іван"}).json()
        response = client.patch(f"/birthdays/{new_birthday.get('_id')}", json={"date": "12.12"})
        assert response.status_code == 200
        assert response.json().get("date") == "12.12"


def test_update_birthday_unexisting():
    with TestClient(app) as client:
        update_birthday_response = client.patch("/birthdays/unexisting_id", json={"date": "12.12"})
        assert update_birthday_response.status_code == 404


def test_delete_birthday():
    with TestClient(app) as client:
        new_birthday = client.post("/birthdays", json={"date": "31.12", "student_name": "Іванов Іван"}).json()
        delete_birthday_response = client.delete(f"/birthdays/{new_birthday.get('_id')}")
        assert delete_birthday_response.status_code == 204


def test_delete_birthday_unexisting():
    with TestClient(app) as client:
        delete_birthday_response = client.delete("/birthdays/unexisting_id")
        assert delete_birthday_response.status_code == 404


def test_bulk_delete_birthdays():
    with TestClient(app) as client:
        ids = [
            client.post("/birthdays", json={"date": "31.12", "student_name": "Іванов Іван"}).json()["_id"],
            client.post("/birthdays", json={"date": "12.12", "student_name": "Іванов Петро"}).json()["_id"]
        ]
        delete_birthdays_response = client.post("/birthdays/bulk", json={"ids": ids})
        assert delete_birthdays_response.status_code == 204
