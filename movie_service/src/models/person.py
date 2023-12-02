from models.film import BaseProjectModel


class PersonRoles(BaseProjectModel):
    """Список ролей, которые персона исполнила в конкретном кинопроизведении"""
    roles: list[str] | None


class Person(BaseProjectModel):
    """
    Модель ответов для:
    /api/v1/persons/search/
    /api/v1/persons/<uuid:UUID>/
    /api/v1/persons/<uuid:UUID>/film/
    """
    full_name: str
    films: list[PersonRoles]
