import logging
import random
import time
from functools import wraps
import psycopg2
import requests


# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=1):
    """
        Функция для повторного выполнения функции через некоторое время, если возникла ошибка. 
        Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

        Формула:
            t = start_sleep_time * (factor ^ n), если t < border_sleep_time
            t = border_sleep_time, иначе
        :param start_sleep_time: начальное время ожидания
        :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
        :param border_sleep_time: максимальное время ожидания
        :return: результат выполнения функции
    """
    def _backoff(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            sleep_time = start_sleep_time
            jitter = random.random()
            while sleep_time < border_sleep_time:
                try:
                    return func(*args, **kwargs)
                except (psycopg2.OperationalError, requests.exceptions.ConnectionError) as e:
                    logger.error(e)
                    sleep_time = start_sleep_time * (factor ** n) + jitter
                    time.sleep(sleep_time)
                    n += 1

            raise ConnectionError

        return inner
    return _backoff
