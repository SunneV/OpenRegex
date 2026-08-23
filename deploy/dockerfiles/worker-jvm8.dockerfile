# --- BUILDER STAGE ---
# JDK 17 still accepts --release 8; the runtime below is a real Java 8 JRE.
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY workers/worker-jvm8/pom.xml ./workers/worker-jvm8/
WORKDIR /app/workers/worker-jvm8
RUN mvn dependency:go-offline

COPY workers/worker-jvm8/src ./src
RUN mvn clean package -DskipTests

# --- PRODUCTION STAGE ---
FROM eclipse-temurin:8-jre-alpine AS production
WORKDIR /app
COPY --from=builder /app/workers/worker-jvm8/target/openregex-worker-jvm8-*-jar-with-dependencies.jar ./worker.jar
ENV WORKER_VERSION="1.0.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}

CMD ["java", "-jar", "worker.jar"]
