from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from services.person import PersonService, get_person_service
from services.film import FilmService, get_film_service
from models.film import FilmShort
from models.person import Person


router = APIRouter()


DETAIL = 'persons not found'


@router.get(
    '/search',
    response_model=list[Person],
    summary='Поиск персон',
    description='Выполняет полнотекстовый поиск персон',
    response_description='Список персон со списком фильмов и ролей, исполненных в них'
)
async def search_persons(
    query: Annotated[str, Query(description='Текст запроса для поиска')],
    page_size: Annotated[int, Query(description='Размер страницы', ge=1)] = 50,
    page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
    person_service: PersonService = Depends(get_person_service)
) -> list[Person]:
    persons = await person_service.get_persons_by_query(
        query, page_size, page_number
    )
    if not persons:
        return []

    return [
        Person.model_validate_json(person.model_dump_json())
        for person in persons
    ]


@router.get(
    '/{person_id}',
    response_model=Person,
    summary='Информация о персоне',
    description='Получение подробной информации о конкретной персоне',
    response_description='Информация о персоне'
)
async def person_details(
    person_id: Annotated[UUID, Path(description='Идентификатор пользователя')],
    person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=DETAIL,
        )

    return Person.model_validate_json(person.model_dump_json())


@router.get(
    '/{person_id}/film',
    response_model=list[FilmShort],
    summary='Информация о фильмах, где участвовала конкретная персона',
    description='Получение списка фильмов, где участвовала конкретная персона',
    response_description='Список фильмов, где участвовала конкретная персона'
)
async def person_films(
    person_id: Annotated[UUID, Path(description='Идентификатор пользователя')],
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service)
) -> list[FilmShort]:
    person = await person_service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='person not found'
        )

    person_films = await film_service.get_person_films(person)

    if not person_films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=DETAIL,
        )
    return [
        FilmShort(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in person_films
    ]
