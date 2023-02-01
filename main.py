import requests
import db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.crud import router as crud_router
from routes.schedule import router as schedule_router

from deta import App

app = App(FastAPI(docs_url=None))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://ki2helper.pp.ua", "https://ki2helper.pp.ua",
        "http://ki2admin.deta.dev", "https://ki2admin.deta.dev",
        "http://ki2helper.deta.dev", "https://ki2helper.deta.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("shutdown")
def shutdown_db_client():
    db.client.close()


@app.lib.run()
@app.lib.cron()
def cron(event):
    requests.post("https://ki2admin.deta.dev/ping")
    requests.post("https://ki2helper.deta.dev/ping")


app.include_router(schedule_router)
app.include_router(crud_router)
app.include_router(auth_router)
app.include_router(admin_router)
