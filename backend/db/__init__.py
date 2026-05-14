from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
# from sqlmodel import SQLModel

from ..config import *
from .models import *
from .views import *


engine = create_async_engine(config.db.db_url.get_secret_value(), echo=True)


# SQLModel.metadata.create_all(engine)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


Session = asynccontextmanager(get_session)
