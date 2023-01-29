from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import db
from routes.birthday import router as birthday_router
from routes.week import router as week_router
from routes.cron import router as cron_router
from routes.timetable import router as timetable_router
from routes.teacher import router as teacher_router
from routes.lesson import router as lesson_router
from routes.playlist import router as playlist_router
from routes.schedule import router as schedule_router
from routes.auth import router as auth_router
from routes.user import router as user_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://ki2helper.pp.ua", "https://ki2helper.pp.ua",
        "http://panel.ki2helper.pp.ua", "https://panel.ki2helper.pp.ua",
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


app.include_router(birthday_router)
app.include_router(cron_router)
app.include_router(lesson_router)
app.include_router(schedule_router)
app.include_router(playlist_router)
app.include_router(teacher_router)
app.include_router(timetable_router)
app.include_router(week_router)
app.include_router(auth_router)
app.include_router(user_router)
