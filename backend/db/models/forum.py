from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .torrent import Torrent


class ForumBase(SQLModel):
    title: str


class Forum(ForumBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    torrents: list['Torrent'] = Relationship(back_populates='forum')


class ForumPublic(ForumBase):
    id: int


class ForumCreate(ForumBase):
    id: int


__all__ = [
    'ForumBase',
    'Forum',
    'ForumPublic',
    'ForumCreate',
]
