# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

FROM python:3.14.2-slim as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base as poetry
RUN pip install poetry==1.8.5 --no-cache-dir
COPY poetry.lock pyproject.toml /app/
RUN poetry export --without dev -o requirements.txt

FROM base as build
RUN apt-get update && apt-get install gcc git -y --no-install-recommends
COPY --from=poetry /app/requirements.txt /tmp/requirements.txt
RUN cat /tmp/requirements.txt
RUN python -m venv /app/.venv && /app/.venv/bin/pip install -r /tmp/requirements.txt

FROM python:3.14.2-slim as runtime

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
RUN apt-get update && apt-get install git -y

# Creating folders, and files for a project:
COPY src /app
