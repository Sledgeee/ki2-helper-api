import requests
import db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.crud import router as crud_router
from routes.schedule import router as schedule_router
from routes.events import router as events_router

from deta import App

app = App(FastAPI(docs_url=None))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://ki2helper.pp.ua", "https://ki2helper.pp.ua"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("shutdown")
def shutdown_db_client():
    db.client.close()


app.include_router(schedule_router)
app.include_router(events_router)
app.include_router(crud_router)
app.include_router(auth_router)
app.include_router(admin_router)