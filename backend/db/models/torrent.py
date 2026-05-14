from typing import TYPE_CHECKING, Self
from sqlmodel import Relationship, SQLModel, Field
from dataclasses import dataclass
from ..type_decorators import DataclassJSON


if TYPE_CHECKING:
    from .forum import Forum
    from .torrent_duplicate import TorrentDuplicate
    from .torrent_image import TorrentImage


@dataclass
class File:
    name: str
    size: int
    type: str = "file"


@dataclass
class Dir:
    name: str
    contents: list[Self | File] = Field(default_factory=[])
    type: str = "dir"


class TorrentBase(SQLModel):
    forum_id: int | None = Field(default=None, foreign_key='forum.id', ondelete="SET NULL")
    title: str
    content: str
    deleted: bool
    filelist: Dir | File = Field(default_factory=dict, sa_type=DataclassJSON(File, Dir))
    hash: str
    tracker_id: int
    registered_at: int | None = None
    size: int | None = None
    old_hash: str | None = None
    old_title: str | None = None
    old_datetime: int | None = None


class Torrent(TorrentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    duplicates: list['TorrentDuplicate'] = Relationship(back_populates='original', sa_relationship_kwargs={'foreign_keys': '[TorrentDuplicate.original_id]'})
    originals: list['TorrentDuplicate'] = Relationship(back_populates='duplicate', sa_relationship_kwargs={'foreign_keys': '[TorrentDuplicate.duplicate_id]'})
    forum: 'Forum' = Relationship(back_populates='torrents')
    images: list['TorrentImage'] = Relationship(back_populates='torrent', cascade_delete=True)


class TorrentPublic(TorrentBase):
    id: int


class TorrentCreate(TorrentBase):
    id: int


__all__ = [
    'File',
    'Dir',
    'TorrentBase',
    'Torrent',
    'TorrentPublic',
    'TorrentCreate',
]
