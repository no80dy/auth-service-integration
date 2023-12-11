FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r ./integrity/requirements.txt

CMD ["python3", "-m", "pytest", "--setup-show", "-vvs", "-W", "ignore::DeprecationWarning", "./integrity/src"]
