FROM python:latest

EXPOSE 8000

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app

RUN chmod +x django-entrypoint.sh

ENTRYPOINT [ "./django-entrypoint.sh" ]
