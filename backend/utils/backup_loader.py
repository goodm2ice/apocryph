from typing import Callable, overload
from pathlib import Path
import xml.etree.ElementTree as ET
import lzma
from dataclasses import dataclass, field
from enum import IntEnum, auto
from uuid import uuid4, UUID
import logging
from contextlib import contextmanager
from zipfile import ZipFile
import io


class BackupLoaderStatus(IntEnum):
    STARTING = auto()
    FINDING = auto()
    READING = auto()
    PARSING_ERROR = auto()
    FAILED = auto()
    COMPLETED = auto()


@dataclass
class BackupForum:
    id: int
    title: str


@dataclass
class BackupDuplicate:
    id: int
    dup_id: int
    p: int


@dataclass
class BackupFilelist:
    uuid: UUID = field(default_factory=uuid4)
    name: str
    size: int | None = None
    children: list['BackupFilelist'] | None = None


@dataclass
class BackupTorrent:
    id: int
    title: str
    content: str | None = None
    size: int | None = None
    deleted: bool = False
    registred_at: int | None = None
    tracker_id: int | None = None
    hash: str | None = None
    old_hash: str | None = None
    old_title: str | None = None
    old_datetime: int | None = None

    forum: BackupForum | None = None
    duplicate: BackupDuplicate | None = None
    files: BackupFilelist | None = None


@dataclass
class BackupLoaderState:
    status: BackupLoaderStatus = BackupLoaderStatus.STARTING
    total_size: int = 0
    read_size: int = 0
    total_count: int = 0
    handled_count: int = 0


@overload
def int_or_none(x: str) -> int: ...
@overload
def int_or_none(x: None) -> None: ...
def int_or_none(x: str | None) -> int | None:
    return int(x) if x is not None else None


@contextmanager
def backup_open(path: Path, encoding = 'utf-8'):
    match path.suffix:
        case '.xml':
            with open(path, mode='rt', encoding=encoding) as f:
                yield f
        case '.xz' | '.7z':
            with lzma.open(path, mode='rt', encoding=encoding) as f:
                yield f
        case '.zip':
            with ZipFile(str(path), mode='r') as zf:
                finfo = next((f for f in zf.filelist if f.filename.endswith('.xml')), None)
                if finfo is None:
                    raise TypeError('В архиве не найден xml-файл!')
                with zf.open(finfo, mode='r') as fb:
                    with io.TextIOWrapper(fb, encoding=encoding) as f:
                        yield f
        case _:
            raise TypeError('Недопустимый тип файла бэкапа!')


class BackupLoader:
    def __init__(self, handler: Callable[[BackupTorrent, str], None], encoding = 'utf-8', log: logging.Logger | None = None):
        self.handler = handler
        self.encoding = encoding
        self.log = log
        if self.log is None:
            self.log = logging.getLogger(__name__)
            self.log.addHandler(logging.NullHandler())

    def __parse_files(self, root: ET.Element | None) -> BackupFilelist | None:
        if root is None:
            return None
        match root.tag:
            case 'dir':
                return BackupFilelist(
                    name=root.get('name'),
                    children=[self.__parse_files(c) for c in root if c is not None]
                )
            case 'file':
                return BackupFilelist(
                    name=root.get('name'),
                    size=int_or_none(root.get('size'))
                )
            case _:
                self.log.warning(f'Неизвестный тег директории/файла: "{root.tag}"')
                return None

    def parse_entity(self, text: str) -> BackupTorrent:
        root = ET.fromstring(text)
        if root.get('id') is None or root.find('title') is None:
            raise ValueError('Отсутствуют обязательные поля "id" и "title"')
        torrent = BackupTorrent(id=int(root.get('id')), title=root.find('title').text)
        if root.find('content') is not None:
            torrent.content = root.find('content').text
        torrent.size = int_or_none(root.get('size'))
        torrent.registred_at = int_or_none(root.get('unixts'))
        torrent.deleted = root.find('del') is not None
        if root.find('torrent') is not None:
            torrent.hash = root.find('torrent').get('hash')
            torrent.tracker_id = int_or_none(root.find('torrent').get('tracker_id'))
        if root.find('old') is not None:
            torrent.old_hash = root.find('old').get('hash')
            torrent.old_title = root.find('old').text
            torrent.old_datetime = int_or_none(root.find('old').get('unixts'))
        if root.find('forum') is not None:
            torrent.forum = BackupForum(
                id=int_or_none(root.find('forum').get('id')),
                title=root.find('forum').text,
            )
        if root.find('dup') is not None:
            torrent.duplicate = BackupDuplicate(
                id=int_or_none(root.find('dup').get('id')),
                dup_id=torrent.id,
                p=int_or_none(root.find('dup').get('p')),
            )
        torrent.files = self.__parse_files(root.find('file') if root.find('dir') is None else root.find('dir'))
        return torrent

    def load(self, path: Path):
        tag_count = 0
        state = BackupLoaderState(total_size=path.stat().st_size)
        with backup_open(path, encoding=self.encoding) as f:
            last_line: str = ''
            stripped_last: str = ''

            def read_line():
                nonlocal last_line
                nonlocal stripped_last
                last_line = f.readline()
                if not last_line:
                    state.status = BackupLoaderStatus.FAILED
                    self.log.error(f'Файл неожиданно закончился! Прочитано {state.read_size} из {state.total_size}')
                    return state
                stripped_last = last_line.strip()
                state.read_size = f.tell()
            
            while not stripped_last.startswith('<torrents'):
                read_line() # Ищем начало раздела
            
            while True:
                state.status = BackupLoaderStatus.FINDING
                # Ищем начало секции (`<torrent`)
                while not stripped_last.startswith('<torrent') and stripped_last != '</torrents>' or stripped_last.startswith('<torrents'):
                    read_line()
                # Если вместо этого нашли конец раздела (`</torrents>`)
                if stripped_last == '</torrents>':
                    break
                state.status = BackupLoaderStatus.READING
                buffer = ''
                tag_count = 1 # Число открытых тегов `<torrent>``
                while tag_count > 0:
                    buffer += last_line
                    read_line()
                    # Могут быть вложенные теги torrent, недопустимо ошибочно посчитать закрытие вложенного тега за закрытие секции
                    if stripped_last.startswith('<torrent') and not stripped_last.endswith('/>'):
                        tag_count += 1
                    if stripped_last == '</torrent>': # Тег закрылся снижаем число
                        tag_count -= 1
                    elif stripped_last == '</torrents>': # Секция закрылась, данных больше не будет
                        tag_count = 0
                if stripped_last == '</torrents>':
                    buffer += '</torrent>'
                else:
                    buffer += last_line
                try:
                    torrent = self.parse_entity(buffer)
                    self.handler(torrent, hash(buffer))
                    self.log.debug(f'Успешная обработка записи #{state.total_count} ({state.read_size}/{state.total_size})')
                    state.handled_count += 1
                except BaseException as e:
                    state.status = BackupLoaderStatus.PARSING_ERROR
                    self.log.warning(f'Ошибка обработки записи #{state.total_count} ({state.read_size}/{state.total_size}): {e}')
                finally:
                    state.total_count += 1
                yield state
            state.status = BackupLoaderStatus.COMPLETED
            self.log.info(
                'Загрузка бэкапа завершена.'
                f'Успешно загружено {state.handled_count} из {state.total_count} найденных записей.'
                f'Объём прочитанных данных: {state.read_size} из {state.total_size}'
            )
            return state
