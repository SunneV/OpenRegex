# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install required dependencies for downloading and extracting JDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tar \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Download and install JDK 23.0.1
RUN curl -fsSL https://download.java.net/java/GA/jdk23.0.1/c28985cbf10d4e648e4004050f8781aa/11/GPL/openjdk-23.0.1_linux-x64_bin.tar.gz \
    | tar -xz -C /usr/local \
    && ln -s /usr/local/jdk-23.0.1 /usr/local/java

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/local/java
# Add PATH to include Java binaries
ENV PATH="$JAVA_HOME/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define environment variables
ENV OPENREGEX_PORT=5000
ENV OPENREGEX_LOG_LEVEL=INFO
ENV OPENREGEX_TIMEOUT_S=5

# Expose the application port
EXPOSE 5000

# Command to start the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]