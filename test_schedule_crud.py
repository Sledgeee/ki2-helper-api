from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.schedule import router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(router)
test_schedule = {
    "day": "Понеділок",
    "day_number": 1,
    "items": [
        {
            "number": 2,
            "week_type": "Чисельник",
            "lesson": {
                "name": "Lesson 1",
                "short_name": "L1",
                "type": "пр.",
                "teacher": "Іванов І.І.",
                "zoom": "link"
            }
        }
    ]
}


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["MONGO_CONNECTION"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("schedule")


def test_create_schedule():
    with TestClient(app) as client:
        response = client.post("/schedule", json=test_schedule)
        assert response.status_code == 201

        body = response.json()
        print(body)
        assert body.get("day") == test_schedule.get("day")
        assert body.get("day_number") == test_schedule.get("day_number")
        assert len(body.get("items")) == len(test_schedule.get("items"))
        assert "_id" in body


def test_create_schedule_missing_day():
    with TestClient(app) as client:
        response = client.post("/schedule", json={
            "day_number": 1,
            "items": [
                {
                    "number": 2,
                    "week_type": "Чисельник",
                    "lesson": {
                        "name": "Lesson 1",
                        "short_name": "L1",
                        "type": "пр.",
                        "teacher": "Іванов І.І.",
                        "zoom": "link"
                    }
                }
            ]
        })
        assert response.status_code == 422


def test_create_schedule_missing_day_number():
    with TestClient(app) as client:
        response = client.post("/schedule", json={
            "day": "Понеділок",
            "items": [
                {
                    "number": 2,
                    "week_type": "Чисельник",
                    "lesson": {
                        "name": "Lesson 1",
                        "short_name": "L1",
                        "type": "пр.",
                        "teacher": "Іванов І.І.",
                        "zoom": "link"
                    }
                }
            ]
        })
        assert response.status_code == 422


def test_create_schedule_missing_items():
    with TestClient(app) as client:
        response = client.post("/schedule", json={
            "day": "Понеділок",
            "day_number": 1
        })
        assert response.status_code == 422


def test_get_schedule():
    with TestClient(app) as client:
        new_schedule = client.post("/schedule", json=test_schedule).json()
        get_schedule_response = client.get(f"/schedule/{new_schedule.get('_id')}")
        assert get_schedule_response.status_code == 200
        assert get_schedule_response.json() == new_schedule


def test_get_schedule_unexisting():
    with TestClient(app) as client:
        get_schedule_response = client.get("/schedule/unexisting_id")
        assert get_schedule_response.status_code == 404


def test_update_schedule():
    with TestClient(app) as client:
        new_schedule = client.post("/schedule", json=test_schedule).json()
        items = new_schedule["items"]
        items[0]["number"] = 3
        response = client.patch(f"/schedule/{new_schedule.get('_id')}", json={"items": items})
        assert response.status_code == 200
        assert response.json().get("items") == items


def test_update_schedule_unexisting():
    with TestClient(app) as client:
        update_schedule_response = client.patch("/schedule/unexisting_id", json={"day": "Вівторок"})
        assert update_schedule_response.status_code == 404


def test_delete_schedule():
    with TestClient(app) as client:
        new_schedule = client.post("/schedule", json=test_schedule).json()
        delete_schedule_response = client.delete(f"/schedule/{new_schedule.get('_id')}")
        assert delete_schedule_response.status_code == 204


def test_delete_schedule_unexisting():
    with TestClient(app) as client:
        delete_schedule_response = client.delete("/schedule/unexisting_id")
        assert delete_schedule_response.status_code == 404
