from typing import Any, Type
from pathlib import Path
from dataclasses import asdict, is_dataclass
from sqlalchemy.types import JSON, TypeDecorator, String


class PathType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Path(value)
        return value


class DataclassJSON(TypeDecorator):
    impl = JSON
    
    def __init__(self, *dataclass_types: Type, **kwargs):
        super().__init__(**kwargs)
        self.dataclass_types = dataclass_types

    def process_bind_param(self, value: Any, dialect) -> Any:
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        return value

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None or not isinstance(value, dict):
            return value

        i = 0
        while i < len(self.dataclass_types):
            try:
                return self.dataclass_types[i](**value)
            except Exception:
                i += 1

        return value


__all__ = [
    'PathType',
    'DataclassJSON',
]
