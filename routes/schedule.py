import pytz
import db
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from typing import List
from models import Schedule

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.get("/filtered/{week_type}", response_description="List schedule by week type", response_model=List[Schedule])
async def schedule_by_week(week_type):
    schedules = list(db.schedule.find({"$or": [{"week": week_type}, {"week": "-"}]}).sort("number").sort("day_number"))
    return schedules


@router.get("/filtered/today/{week_type}", response_description="List schedule by today and week type",
            response_model=Schedule)
async def schedule_by_day(week_type):
    now = datetime.now(tz=pytz.timezone('Europe/Kiev'))
    if (schedule := db.schedule.find_one({"day_number": now.weekday() + 1,
                                          "$or": [{"week": week_type}, {"week": "-"}]})) is not None:
        return schedule

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule not found")
