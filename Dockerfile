FROM python:latest

WORKDIR /UserServiceApp

RUN pip install poetry

COPY poetry.lock pyproject.toml /UserServiceApp/
COPY /UserServiceApp /UserServiceApp

RUN poetry config virtualenvs.create false && poetry install

RUN rm -r tests
