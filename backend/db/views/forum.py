from ..models import ForumPublic, TorrentPublic


class ForumPublicWithRelations(ForumPublic):
    torrents: list[TorrentPublic] = []


__all__ = [
    'ForumPublicWithRelations',
]
