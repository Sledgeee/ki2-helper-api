import base64

import requests
from telebot import TeleBot
from config import BOT_TOKEN

bot = TeleBot(token=BOT_TOKEN, threaded=False)


def get_photo(user_id):
    photos = requests.get(url=f"https://api.telegram.org/bot{BOT_TOKEN}/getUserProfilePhotos", params={
        "user_id": user_id
    })
    user_photo = "/assets/images/avatars/avatar_default.jpg"
    res = dict(photos.json())
    if res["ok"] is True and res["result"]["total_count"] > 0:
        target_url = bot.get_file_url(res["result"]["photos"][0][0]["file_id"])
        bytes_ = (base64.b64encode(requests.get(target_url).content)).decode()
        user_photo = "data:image/jpeg;base64," + bytes_
    return user_photo


def create_user(user_id):
    user_photo = get_photo(user_id)
    user_info = bot.get_chat_member(user_id, user_id).user
    return {
        "user_id": user_info.id,
        "username": user_info.username,
        "first_name": user_info.first_name,
        "last_name": user_info.last_name,
        "pic": user_photo
    }


def send_otp(user_id, otp):
    bot.send_message(user_id, f"OTP: {otp}")
