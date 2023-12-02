import sys
import uuid
import pytest

from unittest.mock import Mock, patch
from pathlib import Path

from ..testdata.response_data import (
    HTTP_200,
    HTTP_404,
    HTTP_422,
    GENRES_RESPONSE_DATA
)
from ..testdata.es_data import es_genres_data
from ..settings import test_settings

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.genre import (
    GenreService,
    CacheGenreHandler,
    ElasticGenreHandler
)


@pytest.mark.parametrize(
    'genre_data, expected_genre_data',
    [
        (
            {'genre_id': es_genres_data[0]['id']},
            {'status': HTTP_200, 'body': GENRES_RESPONSE_DATA[0]}
        ),
        (
            {'genre_id': es_genres_data[1]['id']},
            {'status': HTTP_200, 'body': GENRES_RESPONSE_DATA[1]}
        ),
        (
            {'genre_id': str(uuid.uuid4())},
            {'status': HTTP_404, 'body': {'detail': 'genres not found'}}
        ),
    ]
)
async def test_get_genre_by_id_positive(
    make_get_request,
    es_write_data,
    genre_data,
    expected_genre_data
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    genre_id = genre_data.get('genre_id')
    response = await make_get_request(f'genres/{genre_id}', {})

    assert (
        response.get('status') == expected_genre_data.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        response.get('body') == expected_genre_data.get('body')
    ), 'Тело жанра в ответе должно быть идентично ожидаемому жанру'


@pytest.mark.parametrize(
    'genre_data, expected_http_code',
    [
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 123},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        )
    ]
)
async def test_get_genre_by_genre_id_negative(
    make_get_request,
    es_write_data,
    genre_data,
    expected_http_code
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    genre_id = genre_data.get('genre_id')
    response = await make_get_request(f'genres/{genre_id}', {})

    assert (
        response.get('status') == expected_http_code.get('status')
    ), 'При передаче невалидных данных ответ должен быть равным HTTP_422'


@pytest.mark.parametrize(
    'expected_genre_data',
    [
        (
            {'status': HTTP_200, 'length': 50}
        )
    ]
)
async def test_get_all_genres(
    make_get_request,
    es_write_data,
    expected_genre_data
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    response = await make_get_request('genres/', {})

    assert (
        response.get('status') == expected_genre_data.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        len(response.get('body')) == expected_genre_data.get('length')
    ), 'Количество фильмов в ответе должно быть равно количеству ожидаемых'


async def test_get_film_from_cache(
    make_get_request,
    es_write_data
):
    storage_handler_mock = Mock(spec=ElasticGenreHandler)
    cache_handler_mock = Mock(spec=CacheGenreHandler)
    film_service = GenreService(cache_handler_mock, storage_handler_mock)

    genre_id_mock = uuid.uuid4()

    with (patch.object(
        cache_handler_mock, 'get_genre', return_value='cache data'
    ) as get_film_mock, patch.object(
        storage_handler_mock, 'get_genre_by_id', return_value='storage_data'
    ) as get_film_by_id_mock):
        result = await film_service.get_genre_by_id(genre_id_mock)

        assert (
            get_film_mock.call_count == 1
        ), 'Получение фильма из кэша происходит только один раз'
        assert (
            get_film_by_id_mock.call_count == 0
        ), 'Получение кинопроизведения из хранилища не должно происходить'
        assert (
            result == 'cache data'
        ), 'Данные из кэша должны быть идентичны результату выполнения get_film_by_id'
