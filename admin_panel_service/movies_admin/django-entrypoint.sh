#!/usr/bin/env bash

python3 manage.py collectstatic
python3 manage.py makemigrations admin auth contenttypes sessions messages staticfiles users
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8001
