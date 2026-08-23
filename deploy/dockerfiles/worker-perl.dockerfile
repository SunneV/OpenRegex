# --- PRODUCTION STAGE ---
FROM perl:5.40-slim AS production
WORKDIR /app

COPY workers/worker-perl/cpanfile ./
RUN cpanm --notest --quiet --installdeps . && rm -rf /root/.cpanm

COPY workers/worker-perl/src ./src

ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["perl", "src/worker_runner.pl"]
