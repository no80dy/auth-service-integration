FROM python:latest

EXPOSE 8000

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app

CMD [ "python3", "manage.py", "collectstatic" ]

CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8001" ]
