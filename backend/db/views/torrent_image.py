from ..models import TorrentImagePublic, TorrentPublic, ImagePublic


class TorrentImagePublicWithRelations(TorrentImagePublic):
    torrent: TorrentPublic
    image: ImagePublic


__all__ = [
    'TorrentImagePublicWithRelations',
]
