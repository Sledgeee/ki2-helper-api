import random
import db
from fastapi import APIRouter, status, Request, Response, Body, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from config import JWT_REFRESH_SECRET_KEY
from models import Login, LoginAttempt, Admin
from security import create_access_token, JwtPayload, create_refresh_token, \
    REFRESH_TOKEN_EXPIRE_MINUTES, decode_jwt
from utils import create_user, send_otp

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login",
             response_description="Login user",
             status_code=status.HTTP_200_OK,
             response_class=JSONResponse)
async def login(background_tasks: BackgroundTasks, login_body: Login = Body(...)):
    if (admin := db.admins.find_one({"username": login_body.username})) is not None:
        db.login_attempts.delete_many({"user_id": admin["user_id"]})

        otp = random.randint(100000, 999999)
        login_attempt = LoginAttempt(
            user_id=admin["user_id"],
            otp=otp
        )
        login_attempt = jsonable_encoder(login_attempt)
        new_attempt = db.login_attempts.insert_one(login_attempt)

        background_tasks.add_task(
            send_otp,
            admin["user_id"],
            otp
        )

        return {"accepted": True, "user_id": admin["user_id"], "attempt_id": new_attempt.inserted_id}
    return {"accepted": False}


@router.post("/check-otp",
             response_description="Check OTP",
             status_code=status.HTTP_200_OK)
async def check_otp(response: Response,
                    background_tasks: BackgroundTasks,
                    login_attempt: LoginAttempt = Body(...)):
    attempt = db.login_attempts.find_one({"_id": login_attempt.id})
    if attempt is not None and attempt['otp'] == login_attempt.otp:
        background_tasks.add_task(db.login_attempts.delete_one, {"_id": login_attempt.id})
        user = create_user(login_attempt.user_id)
        payload = JwtPayload(
            sub=str(user["user_id"]),
            username=user["username"],
            first_name=user["first_name"],
            last_name=user["last_name"]
        )
        token = create_access_token(payload)
        response.set_cookie(
            key="AUTH",
            value="true",
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            samesite='none',
            secure=True
        )
        response.set_cookie(
            key="REFRESH_TOKEN",
            value=create_refresh_token(str(user["user_id"])),
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,
            samesite='none',
            httponly=True
        )
        return {"success": True, "user": user, "token": token}

    return {"success": False}


@router.post("/register",
             response_description="Register admin",
             status_code=status.HTTP_201_CREATED,
             response_class=JSONResponse)
async def register(admin: Admin = Body(...)):
    if db.admins.find_one({"user_id": admin.user_id}):
        return {"message": "account exists"}

    if db.admins.find_one({"username": admin.username}):
        return {"message": "username taken"}

    admin = jsonable_encoder(admin)
    new_admin = db.admins.insert_one(admin)
    created_admin = db.admins.find_one(
        {"_id": new_admin.inserted_id}
    )
    return created_admin


@router.post('/refresh')
async def refresh(request: Request, response: Response):
    if (rt := request.cookies.get("REFRESH_TOKEN")) is not None:
        if (rt_payload := decode_jwt(rt, JWT_REFRESH_SECRET_KEY)) is not None:
            user_id = rt_payload['sub']
            user = create_user(user_id)
            payload = JwtPayload(
                sub=str(user["user_id"]),
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"]
            )
            token = create_access_token(payload)
            response.set_cookie(
                key="AUTH",
                value="true",
                samesite="none",
                secure=True,
                max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60
            )
            response.set_cookie(
                key="REFRESH_TOKEN",
                value=create_refresh_token(str(user["user_id"])),
                max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                samesite="none",
                secure=True,
                httponly=True
            )
            return {"token": token}
    return Response(content={"detail": "Not authenticated"}, status_code=status.HTTP_401_UNAUTHORIZED)


@router.post('/logout',
             response_description="Logout admin",
             status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.set_cookie(
        key="AUTH",
        max_age=0,
        samesite="none",
        secure=True,
    )
    response.set_cookie(
        key="REFRESH_TOKEN",
        max_age=0,
        samesite="none",
        secure=True,
        httponly=True
    )
