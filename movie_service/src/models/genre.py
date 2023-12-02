from models.base import BaseProjectModel


class Genres(BaseProjectModel):
    """
    Схемы ответов для:
    /api/v1/genres/
    /api/v1/genres/<uuid:UUID>/
    """
    name: str
