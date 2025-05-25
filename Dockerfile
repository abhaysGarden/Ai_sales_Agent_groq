# Base image with Python 3.10
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install FAISS (CPU version)
RUN pip install --no-cache-dir faiss-cpu

# Copy requirements (if you have one)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code into container
COPY . .

# Expose API port
EXPOSE 8000

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.api.routes:router", "--host", "0.0.0.0", "--port", "8000"]
