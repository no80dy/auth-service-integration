import json

import requests
from requests.exceptions import RequestException


es_url = 'http://127.0.0.1:9200'

# Создаем схему es
with open('./es_schema_movies.json', 'r') as f:
    es_schema_movies = f.read()

try:
    r = requests.put(f'{es_url}/movies',
                     headers={'Content-Type': 'application/json'}, data=es_schema_movies.encode('utf-8'))

    response = json.loads(r.text)
    print(response)
    print(f'Elasticsearch schema movies is created')
except Exception as e:
    print('error_schema:', e)

# грузим данные о фильмах
with open('./es_bulk_dump.json', 'r') as f:
    es_dump_movies = json.load(f)

try:
    r = requests.post(
        f'{es_url}/_bulk', headers={'Content-Type': 'application/json'}, data=es_dump_movies.encode('utf-8'))

    response = json.loads(r.text)
    if response['errors']:
        print(response)

    print(f'Index movies is updated')
except Exception as e:
    print('error_dump:', e)
