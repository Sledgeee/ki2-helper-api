import uuid
import random
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Job(BaseModel):
    run: int = Field(...)
    description: str = Field(...)


class CronJobs(BaseModel):
    check_schedule: Job = Field(...)
    new_year: Job = Field(...)
    check_birthday: Job = Field(...)
    swap_week: Job = Field(...)


class Cron(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    run: int = Field(...)
    jobs: CronJobs = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
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
                    },
                }
            }
        }


class CronUpdate(BaseModel):
    run: Optional[int]
    jobs: Optional[CronJobs]

    class Config:
        schema_extra = {
            "example": {
                "run": 0,
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
                    },
                }
            }
        }


class Birthday(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    student_name: str = Field(...)
    date: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "date": "31.12",
                "student_name": "Іванов Іван"
            }
        }


class BirthdayUpdate(BaseModel):
    student_name: Optional[str]
    date: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "date": "31.12",
                "student_name": "Іванов Петро"
            }
        }


class Playlist(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    link: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "link": "https://www.youtube.com/playlist?list=link1"
            }
        }


class PlaylistUpdate(BaseModel):
    link: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "link": "https://www.youtube.com/playlist?list=link2"
            }
        }


class Lesson(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    short_name: str = Field(...)
    type: str = Field(...)
    teacher: str = Field(...)
    zoom: str = Field(default="немає")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Назва предмета",
                "short_name": "НП",
                "type": "пр.",
                "teacher": "Іванов І.І.",
                "zoom": "посилання"
            }
        }


class LessonUpdate(BaseModel):
    name: Optional[str]
    short_name: Optional[str]
    type: Optional[str]
    teacher: Optional[str]
    zoom: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "Назва предмета 2",
                "short_name": "НП2",
                "type": "лаб.",
                "teacher": "Іванов І.І.",
                "zoom": "посилання 2"
            }
        }


class Teacher(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Іванов І.І."
            }
        }


class TeacherUpdate(BaseModel):
    name: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "Іванов О.І."
            }
        }


class Week(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    type: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "type": "Чисельник"
            }
        }


class WeekUpdate(BaseModel):
    type: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "type": "Знаменник"
            }
        }


class TimetableItem(BaseModel):
    number: int = Field(...)
    start_hour: int = Field(...)
    start_minute: int = Field(...)
    end_hour: int = Field(...)
    end_minute: int = Field(...)
    break_: int = Field(alias="break")


class Timetable(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    items: List[TimetableItem] = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "items": [
                    {
                        "number": 1,
                        "start_hour": 8,
                        "start_minute": 0,
                        "end_hour": 9,
                        "end_minute": 20,
                        "break": 15
                    },
                    {
                        "number": 2,
                        "start_hour": 9,
                        "start_minute": 35,
                        "end_hour": 10,
                        "end_minute": 55,
                        "break": 15
                    }
                ]
            }
        }


class ScheduleItem(BaseModel):
    number: int = Field(...)
    week_type: str = Field(...)
    lesson: Lesson = Field(...)


class Schedule(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    day: str = Field(...)
    day_number: int = Field(...)
    items: List[ScheduleItem] = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
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


class ScheduleUpdate(BaseModel):
    day: Optional[str]
    day_number: Optional[int]
    items: Optional[List[ScheduleItem]]

    class Config:
        schema_extra = {
            "day": "Понеділок",
            "day_number": 1,
            "items": [
                {
                    "number": 3,
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


class Login(BaseModel):
    username: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "username": "@tgadmin"
        }


def gen_otp():
    return random.randint(100000, 999999)


class LoginAttempt(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    user_id: int = Field(...)
    username: str = Field(...)
    otp: int = Field(default_factory=gen_otp)
    is_magic: bool = Field(default=False)
    message_id: int = Field(default=0)
    attempt_date: str = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
            "user_id": 537259225,
            "otp": 202451,
            "is_magic": False,
            "message_id": -1523552,
            "attempt_date": "30.01.2023 00:50:23"
        }


class Admin(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    user_id: int = Field(...)
    username: str = Field(...)
    role: str = Field(default="manager")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
            "user_id": 537259225,
            "username": "panelusername",
            "role": "manager"
        }


class BulkDelete(BaseModel):
    ids: List[str] = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "ids": ["066de609-b04a-4b30-b46c-32537c7f1f6e", "066de609-b04a-4b30-b46c-78273l1j8j1b"]
        }
