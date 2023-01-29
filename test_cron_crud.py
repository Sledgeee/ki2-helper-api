from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.cron import router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(router)
test_cron = {
    "run": 1,
    "jobs": {
        "check_schedule": {
            "run": 0,
            "description": "text 1"
        },
        "new_year": {
            "run": 0,
            "description": "text 2"
        },
        "check_birthday": {
            "run": 1,
            "description": "text 3"
        },
        "swap_week": {
            "run": 1,
            "description": "text 4"
        }
    }
}


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["MONGO_CONNECTION"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("cron")


def test_get_cron():
    with TestClient(app) as client:
        new_cron = client.post("/cron", json=test_cron).json()
        get_cron_response = client.get(f"/cron/{new_cron.get('_id')}")
        assert get_cron_response.status_code == 200
        assert get_cron_response.json() == new_cron


def test_get_cron_unexisting():
    with TestClient(app) as client:
        get_cron_response = client.get("/cron/unexisting_id")
        assert get_cron_response.status_code == 404


def test_update_cron():
    with TestClient(app) as client:
        new_cron = client.post("/cron", json=test_cron).json()
        response = client.patch(f"/cron/{new_cron.get('_id')}", json={"run": 0})
        assert response.status_code == 200
        assert response.json().get("jobs")["check_schedule"]["run"] == 0
        assert response.json().get("run") == 0


def test_update_cron_unexisting():
    with TestClient(app) as client:
        update_cron_response = client.patch("/cron/unexisting_id", json={"run": 0})
        assert update_cron_response.status_code == 404


def test_delete_cron():
    with TestClient(app) as client:
        new_cron = client.post("/cron", json=test_cron).json()
        delete_cron_response = client.delete(f"/cron/{new_cron.get('_id')}")
        assert delete_cron_response.status_code == 204


def test_delete_cron_unexisting():
    with TestClient(app) as client:
        delete_cron_response = client.delete("/cron/unexisting_id")
        assert delete_cron_response.status_code == 404
