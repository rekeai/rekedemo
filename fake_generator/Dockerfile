# Base image
FROM python:3.11-slim

# Install system dependencies for video/image processing
RUN apt-get update && \
    apt-get install -y ffmpeg libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install first (cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Expose Streamlit port
EXPOSE 8501

# Default environment variables
ENV REKE_API_URL="http://localhost:8000" \
    REKE_ORIGIN="Fake AI Generator"

# Command to run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
