FROM python:3.14-slim AS production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml .
COPY libs/python-shared libs/python-shared/
COPY workers/worker-mysql workers/worker-mysql/

RUN uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ./libs/python-shared && \
    uv pip install --system -e ./workers/worker-mysql

WORKDIR /app/workers/worker-mysql/src
ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["python", "worker_runner.py"]
