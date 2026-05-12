from ..models import ImagePublic, TorrentImagePublic


class ImagePublicWithRelations(ImagePublic):
    instances: list[TorrentImagePublic] = []


__all__ = [
    'ImagePublicWithRelations',
]
