FROM python:3.14-slim AS production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# The engines are the real GNU binaries; grep and sed ship with the base image,
# gawk is needed for the three-argument match() that reports group positions.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gawk \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Character-based offsets from the tools require a UTF-8 locale.
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

COPY pyproject.toml .
COPY libs/python-shared libs/python-shared/
COPY workers/worker-posix workers/worker-posix/

RUN uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ./libs/python-shared && \
    uv pip install --system -e ./workers/worker-posix

WORKDIR /app/workers/worker-posix/src
ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["python", "worker_runner.py"]
