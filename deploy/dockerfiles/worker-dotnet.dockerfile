# --- BUILDER STAGE ---
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS builder
WORKDIR /app
COPY workers/worker-dotnet/worker-dotnet.csproj ./workers/worker-dotnet/
WORKDIR /app/workers/worker-dotnet
RUN dotnet restore

COPY workers/worker-dotnet/ ./
RUN dotnet publish -c Release -o /out

# --- PRODUCTION STAGE ---
FROM mcr.microsoft.com/dotnet/runtime:10.0 AS production
WORKDIR /app
COPY --from=builder /out .
ENV WORKER_VERSION="1.3.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}


ENTRYPOINT ["dotnet", "worker-dotnet.dll"]