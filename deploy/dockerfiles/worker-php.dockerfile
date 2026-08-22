# --- BUILDER STAGE ---
FROM composer:2.7 AS builder
WORKDIR /app
COPY workers/worker-php/composer.json ./
RUN composer install --no-dev --ignore-platform-reqs

# --- PRODUCTION STAGE ---
FROM php:8.5-cli-alpine AS production
WORKDIR /app

# Copy Composer dependencies and source code
COPY --from=builder /app/vendor ./vendor
COPY workers/worker-php/src ./src

ENV WORKER_VERSION="1.2.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["php", "src/worker_runner.php"]