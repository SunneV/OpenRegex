# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install required dependencies for JDK, Node.js, and general system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tar \
    xz-utils \
    g++ \
    ca-certificates \
    gnupg \
    dirmngr \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Download and install JDK 23.0.1
RUN curl -fsSL https://download.java.net/java/GA/jdk23.0.1/c28985cbf10d4e648e4004050f8781aa/11/GPL/openjdk-23.0.1_linux-x64_bin.tar.gz \
    | tar -xz -C /usr/local \
    && ln -s /usr/local/jdk-23.0.1 /usr/local/java

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/local/java
# Add Java to PATH
ENV PATH="$JAVA_HOME/bin:$PATH"

# Download and install Node.js v22.14.0
RUN curl -fsSL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz \
    | tar -xJ -C /usr/local \
    && ln -s /usr/local/node-v22.14.0-linux-x64 /usr/local/node

# Set Node.js environment variables
ENV NODE_HOME=/usr/local/node
ENV PATH="$NODE_HOME/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define environment variables
ENV OPENREGEX_PORT=5000
ENV OPENREGEX_LOG_LEVEL=ERROR
ENV OPENREGEX_TIMEOUT_S=5
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=4

# Expose the application port
EXPOSE 5000

# Command to start the application using gunicorn
CMD gunicorn --bind 0.0.0.0:5000 --workers ${GUNICORN_WORKERS} --threads ${GUNICORN_THREADS} app:app
