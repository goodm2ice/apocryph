from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .routers import routers
from .schedule import JobController

FRONTEND_DIR = Path('./frontend/dist')

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


if FRONTEND_DIR.exists():
    print('Найден фронтэнд!')
    @app.get('/{full_path:path}', include_in_schema=False)
    async def frontend(full_path: str):
        path = FRONTEND_DIR.joinpath(full_path)
        if not path.exists() or not path.is_file():
            path = FRONTEND_DIR.joinpath('index.html')
        return FileResponse(path.absolute())
else:
    print('Фронтэнд не найден!')
