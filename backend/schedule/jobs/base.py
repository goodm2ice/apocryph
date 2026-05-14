from ..models import *

class JobMeta(type):
    """ Надтип для базового класса узла """
    type_id: str = 'meta_job'
    visible_name: str = 'MetaJob'
    description: str | None = None
    default_schedule: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob = IntervalJob(hours=24)
    user_visible: bool = True

    def __repr__(cls):
        tid = 'ABSTRACT' if cls.type_id is None else f'id={cls.type_id}'
        desc = '' if cls.description is None else f'=> {cls.description}'
        return f'({cls.__name__})[{tid}]: {cls.visible_name} {desc}'

    def __str__(cls):
        return repr(cls)

    @property
    def metadata(cls) -> dict[str, type['JobBase']]:
        """ Возвращает словарь из всех созданных дочерних классов с ключом в виде их id """
        return { c.type_id: c for c in cls.__subclasses__() if c.type_id is not None }


class JobBase(metaclass=JobMeta):
    def __init_subclass__(
            cls, /,
            id: str,
            name: str,
            description: str | None = None,
            default_schedule: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob | None = None,
            user_visible: bool = True,
            **kwargs):
        super().__init_subclass__(**kwargs)
        cls.type_id = id
        cls.visible_name = name or cls.__name__
        cls.description = description
        cls.default_schedule = default_schedule or IntervalJob(hours=24)
        cls.user_visible = user_visible
        if id is not None and any((c.type_id == id and c != cls for c in JobBase.__subclasses__())):
            raise ValueError(f'Задача с ID={id} уже существует!')

    def __init__(self, schedule: CombinedJob | IntervalJob | CalendarIntervalJob | DateJob | CronJob, *args, **kwargs):
        self.schedule = schedule

    async def run(self):
        raise NotImplementedError('Вызов задачи ещё не описан!')


__all__ = ['JobBase']
