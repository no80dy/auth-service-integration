import sys
import uuid
import pytest

from unittest.mock import Mock, patch
from pathlib import Path

from ..settings import test_settings
from ..testdata.es_data import es_films_data
from ..testdata.response_data import (
    HTTP_200,
    HTTP_404,
    HTTP_422,
    FILMS_RESPONSE_DATA,
    FILMS_SHORT_RESPONSE_DATA
)

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.film import (
    FilmService,
    CacheFilmHandler,
    ElasticFilmHandler
)


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': es_films_data[0]['id']},
            {'status': HTTP_200, 'body': FILMS_RESPONSE_DATA[0]}
        ),
        (
            {'film_id': es_films_data[1]['id']},
            {'status': HTTP_200, 'body': FILMS_RESPONSE_DATA[1]}
        ),
        (
            {'film_id': str(uuid.uuid4())},
            {'status': HTTP_404, 'body': {'detail': 'films not found'}}
        )
    ]
)
async def test_search_film_by_film_id_positive(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    film_id = film_data.get('film_id')
    response = await make_get_request(f'films/{film_id}', {})

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        response.get('body') == expected_answer.get('body')
    ), 'Тело фильма в ответе должно быть идентично ожидаемому фильму'


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': 'string'},
            {'status': HTTP_422}
        ),
        (
            {'film_id': 0},
            {'status': HTTP_422}
        )
    ]
)
async def test_search_film_by_film_id_negative(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    film_id = film_data.get('film_id')
    response = await make_get_request(f'films/{film_id}', {})

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При передаче невалидных данных ответ должен быть равным HTTP_422'


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 10}
        ),
        (
            {'page_size': 100, 'page_number': 1},
            {'status': HTTP_200, 'length': 50}
        )
    ]
)
async def test_films_pagination_positive(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    response = await make_get_request('films/', film_data)

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        len(response.get('body')) == expected_answer.get('length')
    ), 'Количество фильмов в ответе должно быть равно количеству ожидаемых'


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'page_size': -1, 'page_number': -1},
            {'status': HTTP_422}
        ),
        (
            {'page_size': 'string', 'page_number': 'string'},
            {'status': HTTP_422}
        )
    ]
)
async def test_films_pagination_negative(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    response = await make_get_request('films/', film_data)

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При передаче невалидных данных ответ должен быть равным HTTP_422'


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'genre_id': es_films_data[0]['genres'][0]['id']},
            {'status': HTTP_200, 'body': FILMS_SHORT_RESPONSE_DATA[:1]}
        ),
        (
            {'genre_id': es_films_data[1]['genres'][0]['id']},
            {'status': HTTP_200, 'body': FILMS_SHORT_RESPONSE_DATA[1:2]}
        ),
    ]
)
async def test_get_films_by_genre_id_positive(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    genre_id = film_data.get('genre_id')
    response = await make_get_request('films/', {'genre_id': genre_id})

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        response.get('body') == expected_answer.get('body')
    ), 'Тело ответа должно соответствовать ожидаемому'


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 0},
            {'status': HTTP_422}
        )
    ]
)
async def test_get_films_by_genre_id_negative(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    genre_id = film_data.get('genre_id')
    response = await make_get_request('films/', { 'genre_id': genre_id, })

    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При передаче невалидных данных ответ должен быть равным HTTP_422'


async def test_get_film_from_cache():
    storage_handler_mock = Mock(spec=ElasticFilmHandler)
    cache_handler_mock = Mock(spec=CacheFilmHandler)
    film_service = FilmService(cache_handler_mock, storage_handler_mock)

    film_id_mock = uuid.uuid4()

    with (patch.object(
        cache_handler_mock, 'get_film', return_value='cache data'
    ) as get_film_mock, patch.object(
        storage_handler_mock, 'get_film_by_id', return_value='storage data'
    ) as get_film_by_id_mock):
        result = await film_service.get_film_by_id(film_id_mock)

        assert (
            get_film_mock.call_count == 1
        ), 'Получение фильма из кэша происходит только один раз'
        assert (
            get_film_by_id_mock.call_count == 0
        ), 'Получение кинопроизведения из хранилища не должно происходить'
        assert (
            result == 'cache data'
        ), 'Данные из кэша должны быть идентичны результату выполнения get_film_by_id'
