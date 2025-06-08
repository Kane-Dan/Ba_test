FROM python:3.12-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://install.python-poetry.org | python3 -


WORKDIR /app


ENV PATH="/root/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1


COPY pyproject.toml poetry.lock ./


RUN poetry install --no-root


COPY . .


CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8020", "--reload"]