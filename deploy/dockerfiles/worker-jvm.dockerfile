# --- BUILDER STAGE ---
FROM maven:3.9-eclipse-temurin-25 AS builder
WORKDIR /app
COPY workers/worker-jvm/pom.xml ./workers/worker-jvm/
WORKDIR /app/workers/worker-jvm
RUN mvn dependency:go-offline

COPY workers/worker-jvm/src ./src
RUN mvn clean package -DskipTests

# --- PRODUCTION STAGE ---
FROM eclipse-temurin:26-jre AS production
WORKDIR /app
COPY --from=builder /app/workers/worker-jvm/target/openregex-worker-jvm-*-jar-with-dependencies.jar ./worker.jar
ENV WORKER_VERSION="1.2.0"
ARG WORKER_RELEASE_DATE="Unreleased"
ENV WORKER_RELEASE_DATE=${WORKER_RELEASE_DATE}


CMD ["java", "-jar", "worker.jar"]