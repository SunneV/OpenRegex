# --- BUILDER STAGE ---
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    libre2-dev \
    libboost-regex-dev \
    nlohmann-json3-dev \
    libpcre2-dev \
    libonig-dev \
    libvectorscan-dev

WORKDIR /app
COPY . .
RUN g++ -O3 workers/worker-c-cpp/engines/engine-cpp-re2/main.cpp -o /usr/local/bin/re2_engine -lre2
RUN g++ -O3 workers/worker-c-cpp/engines/engine-cpp-std/main.cpp -o /usr/local/bin/std_engine
RUN g++ -O3 workers/worker-c-cpp/engines/engine-cpp-boost/main.cpp -o /usr/local/bin/boost_engine -lboost_regex
RUN g++ -O3 workers/worker-c-cpp/engines/engine-c-posix/main.cpp -o /usr/local/bin/posix_engine
RUN g++ -O3 workers/worker-c-cpp/engines/engine-c-pcre2/main.cpp -o /usr/local/bin/pcre2_engine -lpcre2-8
RUN g++ -O3 workers/worker-c-cpp/engines/engine-c-onig/main.cpp -o /usr/local/bin/onig_engine -lonig
RUN g++ -O3 workers/worker-c-cpp/engines/engine-cpp-hyperscan/main.cpp -o /usr/local/bin/hyperscan_engine -lhs

# --- PRODUCTION STAGE ---
FROM python:3.14-slim AS production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libre2-dev \
    libboost-regex-dev \
    libpcre2-dev \
    libonig-dev \
    libvectorscan-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/re2_engine /usr/local/bin/re2_engine
COPY --from=builder /usr/local/bin/std_engine /usr/local/bin/std_engine
COPY --from=builder /usr/local/bin/boost_engine /usr/local/bin/boost_engine
COPY --from=builder /usr/local/bin/posix_engine /usr/local/bin/posix_engine
COPY --from=builder /usr/local/bin/pcre2_engine /usr/local/bin/pcre2_engine
COPY --from=builder /usr/local/bin/onig_engine /usr/local/bin/onig_engine
COPY --from=builder /usr/local/bin/hyperscan_engine /usr/local/bin/hyperscan_engine

WORKDIR /app

COPY pyproject.toml .
COPY libs/python-shared libs/python-shared/
COPY workers/worker-c-cpp workers/worker-c-cpp/

RUN uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ./libs/python-shared && \
    uv pip install --system -e ./workers/worker-c-cpp

WORKDIR /app/workers/worker-c-cpp/src
ENV WORKER_VERSION="1.3.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["python", "worker_runner.py"]