## Добавление индекса movies и данных о фильмах в elasticsearch

1) В файле docker-compose.override.yml дожен быть проброшен порт 9200 до elasticsearch
    services:
      elastic:
          ports:
              - "9200:9200"

2) В таком случае elasticsearch будет доступен по адресу http://127.0.0.1:9200

3) Перейти в папку init_es

4) Запустить скрипт init_es_movies.py