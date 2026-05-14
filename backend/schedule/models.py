from typing import Literal, Self
from datetime import datetime

from pydantic import BaseModel
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import AndTrigger, OrTrigger


class IntervalJob(BaseModel):
    type: str = 'interval'
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: datetime | None = None
    end_date: datetime | None = None
    timezone: str | None = None
    jitter: int | None = None


class CalendarIntervalJob(BaseModel):
    type: str = 'calendar_interval'
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hour: int = 0
    minute: int = 0
    second: int = 0
    start_date: datetime | None = None
    end_date: datetime | None = None
    timezone: str | None = None
    jitter: int | None = None


class DateJob(BaseModel):
    type: str = 'date'
    date: datetime


class CronJob(BaseModel):
    type: str = 'cron'
    year: int | str | None = None
    month: int | str | None = None
    day: int | str | None = None
    week: int | str | None = None
    day_of_week: int | str | None = None
    hour: int | str | None = None
    minute: int | str | None = None
    second: int | str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    timezone: str | None = None
    jitter: int | None = None


class CombinedJob(BaseModel):
    type: Literal['combined_and', 'combined_or'] = 'combined_and'
    triggers: list[IntervalJob | DateJob | CronJob | Self]
    jitter: int | None = None


def prepare_trigger(v: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob):
    match v:
        case CombinedJob():
            t = AndTrigger if v.type == 'combined_and' else OrTrigger
            return t(triggers=[prepare_trigger(t) for t in v.triggers], jitter=v.jitter)
        case IntervalJob():
            return IntervalTrigger(**v.model_dump(exclude={'type'}))
        case CalendarIntervalJob():
            return CalendarIntervalTrigger(**v.model_dump(exclude={'type'}))
        case DateJob():
            return DateTrigger(**v.model_dump(exclude={'type'}))
        case CronJob():
            return CronTrigger(**v.model_dump(exclude={'type'}))
        case _:
            raise TypeError('Неизвестный тип триггера')


__all__ = [
    'IntervalJob',
    'CalendarIntervalJob',
    'DateJob',
    'CronJob',
    'CombinedJob',
    'prepare_trigger',
]
