## ------------------------------- Python base Stage ------------------------------ ##
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS python-base

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install --no-install-recommends -y \
        build-essential ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=2.1.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV="${POETRY_HOME}/.venv"
ENV POETRY_CACHE_DIR="${POETRY_HOME}/.cache"
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_REQUESTS_TIMEOUT=100

# Creating a virtual environment just for poetry and install it with pip
RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    # Install zlib_ng & isal for home assistant
    && $POETRY_VENV/bin/pip install -U pip zlib_ng isal \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"


## ------------------------------- Base builder Stage ------------------------------ ##
FROM python-base AS builder-base

WORKDIR /app

# Copy Dependencies
COPY poetry.lock pyproject.toml README.md ./

# [OPTIONAL] Validate the project is properly configured
RUN poetry check


## ------------------------------- Dev Builder Stage ------------------------------ ##
FROM builder-base AS builder-dev

# Install all Dependencies
RUN . $POETRY_VENV/bin/activate \
    && poetry install --no-root --no-interaction


## ------------------------------- Dev Stage ------------------------------ ##
FROM builder-dev AS dev

WORKDIR /app

ENV TZ="Europe/Paris"

# Copy all files of the application
COPY . .

EXPOSE 9123

# Run Application
ENTRYPOINT [ "hass", "--config", "/config", "--debug" ]
