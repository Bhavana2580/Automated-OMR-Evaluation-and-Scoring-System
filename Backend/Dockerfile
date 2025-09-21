# backend/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies needed for OpenCV, pdf2image, and poppler
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirement files first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Environment variables (you can override in docker-compose or kubernetes)
ENV OMR_HOST=0.0.0.0
ENV OMR_PORT=8000
ENV OMR_WORKERS=2
ENV OMR_LOG_LEVEL=info

# Start FastAPI with uvicorn
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]