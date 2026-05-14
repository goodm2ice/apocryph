from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .routers import routers
from .schedule import JobController

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    jobs = JobController(scheduler)
    await jobs.load()
    scheduler.start()
    yield { 'scheduler': scheduler, 'jobs': jobs }
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan, title='YoRuTracker API')


for router in routers:
    app.include_router(router)
