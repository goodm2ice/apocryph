from urllib.parse import quote

def create_magnet_link(tracker_id: int, hash: str, display_name: str | None = None) -> str:
    """
    Создаёт magnet-ссылку на раздачу из параметров

    :param tracker_id: Номер трекера
    :param hash: Хэш раздачи
    :param display_name: Заголовок раздачи
    :returns: Строка magnet-ссылка
    :rtype: str
    """
    dn = quote(display_name) if display_name is not None else ""
    id = "" if tracker_id == 1 else str(tracker_id)
    tr = f'http://bt{id}.t-ru.org/ann?magnet'
    return f'magnet:?xt=urn:btih:{hash}&dn={dn}&tr={tr}'
