from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .torrent import Torrent


class TorrentDuplicateBase(SQLModel):
    probability: float


class TorrentDuplicate(TorrentDuplicateBase, table=True):
    duplicate_id: int | None = Field(default=None, primary_key=True, foreign_key='torrent.id')
    original_id: int | None = Field(default=None, primary_key=True, foreign_key='torrent.id')

    duplicate: 'Torrent' = Relationship(back_populates='originals', sa_relationship_kwargs={'foreign_keys': '[TorrentDuplicate.duplicate_id]'})
    original: 'Torrent' = Relationship(back_populates='duplicates', sa_relationship_kwargs={'foreign_keys': '[TorrentDuplicate.original_id]'})


class TorrentDuplicatePublic(TorrentDuplicateBase):
    duplicate_id: int
    original_id: int


class TorrentDuplicateCreate(TorrentDuplicateBase):
    duplicate_id: int
    original_id: int


__all__ = [
    'TorrentDuplicateBase',
    'TorrentDuplicate',
    'TorrentDuplicatePublic',
    'TorrentDuplicateCreate',
]
