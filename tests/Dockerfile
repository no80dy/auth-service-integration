FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY integrity/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r /app/requirements.txt

COPY . .

CMD ["python3", "-m", "pytest", "--setup-show", "-vvs", "-W", "ignore::DeprecationWarning", "/app/integrity/src"]
