from sqlmodel import delete, or_

from .base import JobBase
from ...db import Session
from ...db.models import *


class DBCleanup(JobBase,
                  id='db_cleanup',
                  name='Подчистить базу данных',
                  description='Удалить ненужные данные в базе'):
    class JobSettings(JobBase.JobSettings):
        cleanup_forums: bool = True
        """ Очищать форумы без раздач """
        cleanup_jobs: bool = True
        """ Очищать неизвестные задачи """
        cleanup_duplicates: bool = True
        """ Очищать записи о дупликатах раздач """

    async def run(self, *args, **kwargs):
        async with Session() as session:
            if self.settings.cleanup_forums:
                query = delete(Forum).where(~Forum.torrents.any())
                await session.exec(query)
            if self.settings.cleanup_jobs:
                query = delete(JobSettings).where(~JobSettings.job_key.in_(JobBase.metadata.keys()))
                await session.exec(query)
            if self.settings.cleanup_duplicates:
                query = delete(TorrentDuplicate).where(or_(TorrentDuplicate.duplicate_id == None, TorrentDuplicate.original_id == None))
                await session.exec(query)

            await session.commit()


__all__ = ['DBCleanup']
