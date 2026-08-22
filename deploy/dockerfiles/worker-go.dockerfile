# --- BUILDER STAGE ---
FROM golang:1.24-alpine AS builder
WORKDIR /app/workers/worker-go

COPY workers/worker-go/go.mod workers/worker-go/go.sum* ./
RUN go mod download

COPY workers/worker-go/ ./
RUN go mod tidy && \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /worker .

# --- PRODUCTION STAGE ---
FROM alpine:latest AS production
WORKDIR /app
COPY --from=builder /worker .
ENV WORKER_VERSION="1.2.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}


CMD ["./worker"]