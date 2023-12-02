import json
import pytest

from ..settings import test_settings
from ..testdata.es_data import es_films_data, es_persons_data
from ..testdata.response_data import HTTP_200, HTTP_422


@pytest.mark.parametrize(
    'query_data, expected_answer, endpoint, data, index',
    [
        # дефолтная пагинация
        (
            {'query': 'Star'},
            {'status': HTTP_200, 'length': 50},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat'},
            {'status': HTTP_200, 'length': 50},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': 'Mashed'},
            {'status': HTTP_200, 'length': 0},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Hello'},
            {'status': HTTP_200, 'length': 0},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': ''},
            {'status': HTTP_200, 'length': 0},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': ''},
            {'status': HTTP_200, 'length': 0},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),

        # передаем значения пагинации
        (
            {'query': 'Star', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 10},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 10},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': 'Star', 'page_size': 100, 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat', 'page_size': 100, 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': 'Mashed', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 0},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'World', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 0},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': '', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 0},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': '', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 0},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),

        # передается часть параметров пагинации
        (
            {'query': 'Star', 'page_size': 10},
            {'status': HTTP_200, 'length': 10},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat', 'page_size': 10},
            {'status': HTTP_200, 'length': 10},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
        (
            {'query': 'Star', 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat', 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
    ]
)
async def test_search_films_positive(
    make_get_request,
    es_write_data,
    query_data,
    expected_answer,
    endpoint,
    data,
    index
):
    # Загружаем данные в ES
    await es_write_data(data, index)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request(endpoint, query_data)

    # 4. Проверяем ответ
    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При позитивном сценарии поиска фильмов, ответ отличается от 200'

    assert (
        len(response.get('body')) == expected_answer.get('length')
    ), 'При позитивном сценарии поиска фильмов, длина тела ответа отличается от ожидаемого'


@pytest.mark.parametrize(
    'query_data, expected_http_code, endpoint',
    [
        # невалидные значения пагинации
        (
            {'query': 'Star', 'page_size': -10, 'page_number': -1},
            HTTP_422,
            'films/search',
        ),
        (
            {'query': 'Mashed', 'page_size': 10, 'page_number': -1},
            HTTP_422,
            'films/search',
        ),
        (
            {'query': '', 'page_size': -10, 'page_number': 1},
            HTTP_422,
            'films/search',
        ),

        (
            {'query': 'Mat', 'page_size': -10, 'page_number': -1},
            HTTP_422,
            'persons/search',
        ),
        (
            {'query': 'Mat', 'page_size': 10, 'page_number': -1},
            HTTP_422,
            'persons/search',
        ),
        (
            {'query': '', 'page_size': -10, 'page_number': 1},
            HTTP_422,
            'persons/search',
        ),

        # передается часть параметров пагинации невалидными
        (
            {'query': 'Star', 'page_size': -10},
            HTTP_422,
            'films/search',
        ),
        (
            {'query': 'Star', 'page_number': -1},
            HTTP_422,
            'films/search',
        ),

        (
            {'query': 'Star', 'page_size': -5},
            HTTP_422,
            'films/search',
        ),

        (
            {'query': 'Star', 'page_size': -10},
            HTTP_422,
            'persons/search',
        ),
        (
            {'query': 'Star', 'page_number': -1},
            HTTP_422,
            'persons/search',
        ),

        (
            {'query': 'Star', 'page_size': -5},
            HTTP_422,
            'persons/search',
        ),
    ]
)
async def test_search_films_negative(
    make_get_request,
    es_write_data,
    query_data,
    expected_http_code,
    endpoint
):
    # Загружаем данные в ES
    await es_write_data(es_films_data, test_settings.es_movies_index)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request(endpoint, query_data)

    # 4. Проверяем ответ
    assert response.get(
        'status') == expected_http_code, 'при невалидных значениях, получен ответ отличный от 422'


@pytest.mark.parametrize(
    'query_data, expected_answer, endpoint, data, index',
    [
        # дефолтная пагинация
        (
            {'query': 'Star', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'films/search',
            es_films_data,
            test_settings.es_movies_index,
        ),
        (
            {'query': 'Mat', 'page_size': 10, 'page_number': 1},
            {'status': HTTP_200, 'length': 50},
            'persons/search',
            es_persons_data,
            test_settings.es_persons_index,
        ),
    ]
)
async def test_search_with_cache(
    redis_client,
    make_get_request,
    es_write_data,
    query_data,
    expected_answer,
    endpoint,
    data,
    index
):
    key_string = f'{query_data.get("query")}/{query_data.get("page_size")}/{query_data.get("page_number")}'
    key = bytes(key_string, 'utf-8')
    await redis_client.set(key, '')

    await make_get_request(endpoint, query_data)

    value = await redis_client.get(key)
    str1 = value.decode('UTF-8')
    dict_str = json.loads(str1)
    list_of_dicts = [json.loads(s) for s in dict_str]

    assert (
        list_of_dicts == data[:query_data.get('page_size')]
    ), 'В кэше значения после вызова эндпоинта search не соответствуют ожидаемым'
