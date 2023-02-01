from datetime import datetime

import db
from fastapi import APIRouter, status, Body, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import Login, LoginAttempt, Admin
from security import create_access_token, JwtPayload
from utils import create_user, send_otp, send_message

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login",
             response_description="Login user",
             status_code=status.HTTP_200_OK,
             response_class=JSONResponse)
async def login(background_tasks: BackgroundTasks, login_body: Login = Body(...)):
    if (admin := db.admins.find_one({"username": login_body.username})) is not None:
        db.login_attempts.delete_many({"user_id": admin["user_id"]})
        login_attempt = LoginAttempt(
            user_id=admin["user_id"],
            username=admin["username"]
        )
        background_tasks.add_task(
            send_otp,
            admin["user_id"],
            login_attempt.otp
        )
        login_attempt = jsonable_encoder(login_attempt)
        new_attempt = db.login_attempts.insert_one(login_attempt)
        return {"accepted": True, "user_id": admin["user_id"], "attempt_id": new_attempt.inserted_id}
    return {"accepted": False}


@router.post("/check-otp",
             response_description="Check OTP",
             status_code=status.HTTP_200_OK)
async def check_otp(background_tasks: BackgroundTasks,
                    login_attempt: LoginAttempt = Body(...)):
    attempt = db.login_attempts.find_one({"_id": login_attempt.id})
    if attempt is not None and attempt['otp'] == login_attempt.otp:
        background_tasks.add_task(db.login_attempts.delete_one, {"_id": login_attempt.id})
        user = create_user(login_attempt.user_id, login_attempt.username)
        payload = JwtPayload(
            sub=str(login_attempt.user_id),
            username=login_attempt.username
        )
        token = create_access_token(payload)
        return {"success": True, "user": user, "token": token}

    return {"success": False}


@router.post('/cml')
async def create_magic_link(la: LoginAttempt = Body(...)):
    db.login_attempts.delete_many({"user_id": la.user_id})
    endpoint = "https://ki2helper.pp.ua/magic-login"
    message = send_message(la.user_id,
                           "Для авторизації в панель "
                           "використайте посилання нижче (воно дійсне протягом 5 хвилин):\n"
                           f"{endpoint}?uid={la.user_id}&um={la.username}&otp={la.otp}&hash_={la.id}",
                           protect_content=True,
                           disable_web_page_preview=True)
    la.message_id = message.message_id
    la = jsonable_encoder(la)
    db.login_attempts.insert_one(la)


@router.post("/magic-login",
             response_description="Magic login",
             status_code=status.HTTP_200_OK)
async def magic_login(background_tasks: BackgroundTasks, login_attempt: LoginAttempt = Body(...)):
    now = datetime.utcnow()
    attempt = db.login_attempts.find_one({
        "_id": login_attempt.id,
        "user_id": int(login_attempt.user_id),
        "username": login_attempt.username,
        "otp": int(login_attempt.otp),
        "is_magic": bool(login_attempt.is_magic)})
    if not attempt:
        return {"success": False}

    background_tasks.add_task(
        db.login_attempts.delete_one,
        {"_id": login_attempt.id}
    )
    attempt_date = datetime.fromisoformat(attempt['attempt_date'])
    duration = now - attempt_date
    diff = divmod(duration.total_seconds(), 60)[0]
    user = create_user(login_attempt.user_id, login_attempt.username)
    payload = JwtPayload(
        sub=str(login_attempt.user_id),
        username=login_attempt.username
    )
    token = create_access_token(payload)
    if diff <= 5:
        return {"success": True, "user": user, "token": token}
    return {"success": False}


@router.post("/register",
             response_description="Register admin",
             status_code=status.HTTP_201_CREATED)
async def register(admin: Admin = Body(...)):
    if db.admins.find_one({"user_id": admin.user_id}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user_id")

    if db.admins.find_one({"username": admin.username}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username")

    admin = jsonable_encoder(admin)
    new_admin = db.admins.insert_one(admin)
    created_admin = db.admins.find_one(
        {"_id": new_admin.inserted_id}
    )
    return created_admin
