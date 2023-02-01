import base64

import requests
from telebot import TeleBot
from telebot.types import Message

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


def create_user(user_id, username):
    user_photo = get_photo(user_id)
    return {
        "user_id": user_id,
        "username": username,
        "pic": user_photo
    }


def send_otp(user_id, otp):
    bot.send_message(user_id, f"OTP: {otp}")


def send_message(user_id, message, protect_content=False, disable_web_page_preview=False) -> Message:
    return bot.send_message(user_id, message,
                            protect_content=protect_content,
                            disable_web_page_preview=disable_web_page_preview)
