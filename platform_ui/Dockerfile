# Base image
FROM python:3.11-slim

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy UI code
COPY . /app

# Expose Streamlit port
EXPOSE 8502

# Default environment variable for API URL
ENV REKE_API_URL="http://localhost:8000"

# Command to run Streamlit frontend
CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]
