from datetime import datetime

from sqlmodel import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..db import Session
from ..db.models import JobSettings
from .jobs import jobs, JobBase
from .models import *


class JobController:
    jobs: dict[str, JobBase] = {}
    scheduler: AsyncIOScheduler

    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    def __add_job(self, job_key: str, schedule: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob | None = None, settings: dict | str | None = None):
        if job_key not in jobs:
            raise ValueError('Неизвестный ID задачи!')
        if schedule is None:
            schedule = jobs[job_key].default_schedule
        removed = False
        if self.scheduler.get_job(job_id=job_key):
            self.scheduler.remove_job(job_id=job_key)
            removed = True

        self.jobs[job_key] = jobs[job_key](schedule, settings)
        trigger = prepare_trigger(schedule)
        job = self.scheduler.add_job(self.jobs[job_key].run, id=job_key, trigger=trigger)
        print(f'{'Пересоздана' if removed else 'Добавлена'} задача{' по умолчанию' if schedule is None else ''}: {job_key} => {trigger}')
        return job

    async def load(self):
        """ Загрузить задачи из базы """
        try:
            async with Session() as session:
                schedules = await session.exec(select(JobSettings))
                for s in schedules:
                    if s.job_key not in jobs:
                        # TODO: Вывести в логер предупреждение
                        continue
                    self.__add_job(s.job_key, s.schedule, s.settings)
        except Exception:
            pass

        for key in jobs.keys(): # Для всех не имеющих расписание в базе ставим по умолчанию
            if key not in self.jobs:
                self.__add_job(key)

    async def save_all(self):
        """ Сохранить все данные расписаний в базу """
        async with Session() as session:
            records = list(await session.exec(select(JobSettings)))

            keys = []
            for job in records:
                if job.job_key in self.jobs:
                    job.schedule = self.jobs[job.job_key].schedule
                    keys.append(job.job_key)
            
            for key, job in self.jobs.items():
                if key not in keys:
                    records.append(JobSettings(job_key=key, schedule=job.schedule))
                
            await session.add_all(records)
            await session.commit(records)


    async def set_schedule(self, job_key: str, schedule: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob):
        """ Задать расписание задаче """
        job = self.__add_job(job_key, schedule)

        async with Session() as session:
            record = await session.get(JobSettings, job_key)
            if record:
                record.schedule = schedule
            else:
                record = JobSettings(job_key=job_key, schedule=schedule)
            await session.add(record)
            await session.commit()

        return job

    async def run_now(self, job_key: str):
        """ Запустить задачу прямо сейчас """
        if job_key not in jobs:
            raise ValueError('Неизвестный ID задачи!')
        if job_key not in self.jobs:
            return self.__add_job(job_key=job_key, schedule=DateJob(date=datetime.now()))

        return self.scheduler.add_job(self.jobs[job_key].run, 'date', run_date=datetime.now())


__all__ = ['JobController']
