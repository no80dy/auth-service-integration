FROM python:latest

EXPOSE 8000

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]
