FROM python:3.14-slim AS production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# The engine is a real Vim; vim-nox is the headless build with the full
# scripting interface engine.vim relies on.
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim-nox \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

COPY pyproject.toml .
COPY libs/python-shared libs/python-shared/
COPY workers/worker-vim workers/worker-vim/

RUN uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ./libs/python-shared && \
    uv pip install --system -e ./workers/worker-vim

WORKDIR /app/workers/worker-vim/src
ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["python", "worker_runner.py"]
