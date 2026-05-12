from ..models import TorrentPublic, ForumPublic, TorrentImagePublic, TorrentDuplicatePublic


class TorrentPublicWithRelations(TorrentPublic):
    forum: ForumPublic
    images: list[TorrentImagePublic] = []
    duplicates: list[TorrentDuplicatePublic] = []
    originals: list[TorrentDuplicatePublic] = []


__all__ = [
    'TorrentPublicWithRelations',
]
