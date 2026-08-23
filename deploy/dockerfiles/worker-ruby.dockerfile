# --- BUILDER STAGE ---
FROM ruby:3.4-alpine AS builder
WORKDIR /app
COPY workers/worker-ruby/Gemfile ./
RUN apk add --no-cache build-base && \
    bundle config set --local without 'development test' && \
    bundle install

# --- PRODUCTION STAGE ---
FROM ruby:3.4-alpine AS production
WORKDIR /app

COPY --from=builder /usr/local/bundle /usr/local/bundle
COPY workers/worker-ruby/Gemfile ./
COPY workers/worker-ruby/src ./src

ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["ruby", "src/worker_runner.rb"]
