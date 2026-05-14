from sqlmodel import SQLModel, Field

from ..type_decorators import ModelJSON
from ...schedule.models import *


class JobScheduleBase(SQLModel):
    schedule: IntervalJob | CalendarIntervalJob | DateJob | CronJob | CombinedJob = Field(sa_type=ModelJSON(CombinedJob, IntervalJob, CalendarIntervalJob, DateJob, CronJob))


class JobSchedule(JobScheduleBase, table=True):
    job_key: str | None = Field(default=None, primary_key=True)


class JobSchedulePublic(JobScheduleBase):
    job_key: str


class JobScheduleCreate(JobScheduleBase):
    job_key: str


__all__ = [
    'JobScheduleBase',
    'JobSchedule',
    'JobSchedulePublic',
    'JobScheduleCreate',
]
