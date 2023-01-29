from pymongo import MongoClient
from config import MONGO_CONNECTION, DB_NAME

client = MongoClient(MONGO_CONNECTION)
db = client[DB_NAME]

admins = db.get_collection("admins")
birthdays = db.get_collection("birthdays")
cron = db.get_collection("cron")
login_attempts = db.get_collection("login_attempts")
playlists = db.get_collection("playlists")
lessons = db.get_collection("lessons")
schedule = db.get_collection("schedules")
teachers = db.get_collection("teachers")
timetable = db.get_collection("timetable")
week = db.get_collection("weeks")
