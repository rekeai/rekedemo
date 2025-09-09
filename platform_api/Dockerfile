# platform_api/Dockerfile
FROM python:3.11-slim

# Install ffmpeg only (needed for video watermarking)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY . /app

# Expose port
EXPOSE 8000

# Start FastAPI via uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
