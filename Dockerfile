FROM python:3.11-alpine

ENV PYTHONBUFFERED 1
ENV BOT_TOKEN ""
ENV BOT_CHANGE_NAME FALSE
ENV BOT_ALLOWED_USERS ""

WORKDIR /opt/app
RUN adduser -D appuser

# Установка зависимостей
COPY Pipfile.lock .
RUN pip install --upgrade pipenv \
    && pipenv requirements --dev > requirements.txt \
    && pip install -r requirements.txt \
    && pip uninstall -y pipenv \
    && rm requirements.txt Pipfile.lock

COPY . .

USER appuser

CMD python main.py
