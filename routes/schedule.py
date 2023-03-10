import pytz
import db
from datetime import datetime
from fastapi import APIRouter
from typing import List
from models import Schedule

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.get("/", response_description="List schedule")
async def schedule_all():
    schedule = list(db.schedule.find().sort("number").sort("day_number"))
    schedule_to_print = list()
    for item in schedule:
        item_for_print = item
        item_for_print['lesson'] = item['lesson']['short_name'] + ' ' + item['lesson']['type']
        schedule_to_print.append(item_for_print)
    return schedule_to_print


@router.get("/count", response_description="Count documents", response_model=int)
async def count_docs():
    return db.schedule.count({})


@router.get("/filtered/{week_type}", response_description="List schedule by week type", response_model=List[Schedule])
async def schedule_by_week(week_type):
    schedule = list(db.schedule.find({"$or": [{"week_type": week_type}, {"week_type": "-"}]})
                    .sort("number")
                    .sort("day_number"))
    return schedule


@router.get("/filtered/today/{week_type}", response_description="List schedule by today and week type",
            response_model=List[Schedule])
async def schedule_by_day(week_type):
    now = datetime.now(tz=pytz.timezone('Europe/Kiev'))
    schedule = list(db.schedule.find({"day_number": now.weekday() + 1,
                                      "$or": [{"week_type": week_type}, {"week_type": "-"}]})
                    .sort("number"))
    return schedule
