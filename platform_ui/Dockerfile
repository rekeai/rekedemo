# platform_ui/Dockerfile
FROM python:3.11-slim

# Install ffmpeg for video previews
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy UI code
COPY . /app

# Expose port
EXPOSE 8502

# Start Streamlit UI
CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]
