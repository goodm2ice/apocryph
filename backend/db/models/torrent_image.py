from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .image import Image
    from .torrent import Torrent


class TorrentImageBase(SQLModel):
    hash: str | None = Field(default=None, foreign_key='image.hash', ondelete="SET NULL") 


class TorrentImage(TorrentImageBase, table=True):
    torrent_id: int | None = Field(default=None, primary_key=True, foreign_key='torrent.id')
    link: str | None = Field(default=None, primary_key=True)

    image: list['Image'] = Relationship(back_populates='instances')
    torrent: 'Torrent' = Relationship(back_populates='images')


class TorrentImagePublic(TorrentImageBase):
    torrent_id: int
    link: str


class TorrentImageCreate(TorrentImageBase):
    torrent_id: int
    link: str


__all__ = [
    'TorrentImageBase',
    'TorrentImage',
    'TorrentImagePublic',
    'TorrentImageCreate',
]
