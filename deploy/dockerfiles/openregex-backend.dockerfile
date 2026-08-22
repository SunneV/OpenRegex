FROM python:3.14-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Expose globally for both development and production
ENV APP_VERSION="2.3.0"
ARG APP_RELEASE_DATE="Unreleased"
ENV APP_RELEASE_DATE=${APP_RELEASE_DATE}

# --- DEVELOPMENT STAGE ---
FROM base AS development
# Dependencies and source code are mounted at runtime via docker-compose
COPY pyproject.toml .
COPY apps/openregex-backend/pyproject.toml apps/openregex-backend/
COPY libs/python-shared/pyproject.toml libs/python-shared/

WORKDIR /app/apps/openregex-backend/src
CMD ["sh", "-c", "uv pip install --system -e /app/libs/python-shared -e /app/apps/openregex-backend && uvicorn backend_runner:app --host 0.0.0.0 --port 8000 --reload"]

# --- PRODUCTION STAGE ---
FROM base AS production
COPY pyproject.toml .
RUN uv sync
COPY apps/openregex-backend apps/openregex-backend/
COPY libs/python-shared libs/python-shared/

# Install the shared library and the backend directly into the system environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ./libs/python-shared && \
    uv pip install --system -e ./apps/openregex-backend

WORKDIR /app/apps/openregex-backend/src

CMD ["uvicorn", "backend_runner:app", "--host", "0.0.0.0", "--port", "8000"]