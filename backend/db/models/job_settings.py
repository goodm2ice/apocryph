from sqlmodel import SQLModel, Field, JSON

from ..type_decorators import ModelJSON
from ...schedule.models import *


class JobSettingsBase(SQLModel):
    schedule: IntervalJob | CalendarIntervalJob | DateJob | CronJob | CombinedJob = Field(sa_type=ModelJSON(CombinedJob, IntervalJob, CalendarIntervalJob, DateJob, CronJob))
    settings: dict | None = Field(default=None, sa_type=JSON)


class JobSettings(JobSettingsBase, table=True):
    job_key: str | None = Field(default=None, primary_key=True)


class JobSettingsPublic(JobSettingsBase):
    job_key: str


class JobSettingsCreate(JobSettingsBase):
    job_key: str


__all__ = [
    'JobSettingsBase',
    'JobSettings',
    'JobSettingsPublic',
    'JobSettingsCreate',
]
