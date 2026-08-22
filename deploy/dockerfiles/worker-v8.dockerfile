FROM node:24-slim AS production
WORKDIR /app

COPY workers/worker-v8/package*.json ./workers/worker-v8/
WORKDIR /app/workers/worker-v8
RUN npm install

COPY workers/worker-v8/ ./
WORKDIR /app/workers/worker-v8/src

ENV WORKER_VERSION="1.2.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}


CMD ["node", "worker_runner.js"]