from typing import TYPE_CHECKING
from pathlib import Path
from sqlmodel import SQLModel, Field, Relationship
from ..type_decorators import PathType


if TYPE_CHECKING:
    from .torrent_image import TorrentImage


class ImageBase(SQLModel):
    path: Path = Field(sa_type=PathType)


class Image(ImageBase, table=True):
    hash: str | None = Field(default=None, primary_key=True)

    instances: list['TorrentImage'] = Relationship(back_populates='image')


class ImagePublic(ImageBase):
    hash: str


class ImageCreate(ImageBase):
    hash: str


__all__ = [
    'ImageBase',
    'Image',
    'ImagePublic',
    'ImageCreate',
]
