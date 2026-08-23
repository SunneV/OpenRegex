# --- BUILDER STAGE ---
FROM rust:slim AS builder
WORKDIR /app
COPY workers/worker-rust ./workers/worker-rust
WORKDIR /app/workers/worker-rust
RUN cargo build --release

# --- PRODUCTION STAGE ---
FROM debian:bookworm-slim AS production
WORKDIR /app
COPY --from=builder /app/workers/worker-rust/target/release/openregex-worker-rust .
ENV WORKER_VERSION="1.3.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}


CMD ["./openregex-worker-rust"]