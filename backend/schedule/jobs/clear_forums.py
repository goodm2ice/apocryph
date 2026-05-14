from sqlmodel import delete

from .base import JobBase
from ...db import Session
from ...db.models.forum import Forum


class ClearForums(JobBase,
                  id='clear_forums',
                  name='Подчистить форумы',
                  description='Удалить форумы, не связанные ни с одной раздачей'):
    async def run(self, *args, **kwargs):
        async with Session() as session:
            query = delete(Forum).where(~Forum.torrents.any())
            await session.exec(query)
            await session.commit()


__all__ = ['ClearForums']
