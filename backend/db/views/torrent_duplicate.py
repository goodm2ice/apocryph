from ..models import TorrentDuplicatePublic, TorrentPublic


class TorrentDuplicatePublicWithRelations(TorrentDuplicatePublic):
    original: TorrentPublic
    duplicate: TorrentPublic


__all__ = [
    'TorrentDuplicatePublicWithRelations',
]
