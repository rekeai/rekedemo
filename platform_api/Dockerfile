# platform_api/Dockerfile
FROM python:3.11-slim

# Install ffmpeg for video processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy main API code
COPY app.py requirements.txt ./ 

# Copy the SDK folder
COPY sdk ./sdk

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r sdk/requirements.txt

# Expose the API port
EXPOSE 8000

# Start the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
