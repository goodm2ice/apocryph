from .base import JobBase
from .db_cleanup import *

jobs = JobBase.metadata


__all__ = ['jobs']
