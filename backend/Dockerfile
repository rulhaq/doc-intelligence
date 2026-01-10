FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and required directories
RUN groupadd --system app && useradd --system --gid app --home /app app && \
    mkdir -p /data /var/log/customerllm && \
    chown -R app:app /app /data /var/log/customerllm && \
    chmod +x /app/docker-entrypoint.sh

# Run application
USER app
CMD ["sh", "/app/docker-entrypoint.sh"]

