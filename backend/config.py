from pathlib import Path
from enum import StrEnum, auto

from pydantic import Field, IPvAnyAddress, SecretStr, computed_field
from pydantic_settings import BaseSettings as _BaseSettings


class CaseInsensitiveEnum(StrEnum):
    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


class BaseSettings(_BaseSettings):
    class Config:
        extra = 'ignore'


class FastAPISettings(BaseSettings):
    host: IPvAnyAddress = '0.0.0.0'
    port: int = Field(default=5000, ge=0, le=65353)


class DbType(CaseInsensitiveEnum):
    POSTGRES = auto()
    SQLITE = auto()


class DatabaseSettings(BaseSettings):
    username: str = 'postgres'
    password: SecretStr = SecretStr('q')
    host: str = 'db'
    port: int = Field(default=5432, ge=0, le=65353)
    name: str = 'yrt'
    type: DbType = DbType.POSTGRES

    @computed_field
    @property
    def db_url(self) -> SecretStr:
        match self.type:
            case DbType.POSTGRES:
                return SecretStr(f'postgresql+asyncpg://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}')
            case DbType.SQLITE:
                return SecretStr(f'sqlite:///{self.name}')
            case _:
                raise ValueError('Неизвестный тип базы данных')


class MeiliSearchSettings(BaseSettings):
    host: str = 'http://meilisearch:7700'
    master_key: SecretStr


class QBitTorrentSettings(BaseSettings):
    host: str = 'http://qbittorrent:8080'
    username: str = 'admin'
    password: SecretStr


class LogLevel(CaseInsensitiveEnum):
    DEBUG = auto()
    INFO = auto()
    WARN = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class Config(BaseSettings):
    fastapi: FastAPISettings = FastAPISettings()
    db: DatabaseSettings = DatabaseSettings()
    meili: MeiliSearchSettings | None = None
    qbittorrent: QBitTorrentSettings | None = None
    archivepath: Path = '/backup.xz'
    loglevel: LogLevel = LogLevel.INFO

    class Config(BaseSettings.Config):
        env_nested_delimiter = '_'
        env_nested_max_split = 1


config = Config()


__all__ = [
    'config',
]
