FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user and temp directory
RUN groupadd --system app && useradd --system --gid app --home /app app && \
    mkdir -p /tmp/ocr /data && chown -R app:app /app /tmp/ocr /data

# Run application
USER app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${OCR_WORKER_PORT}"]

