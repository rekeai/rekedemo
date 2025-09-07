# Use lightweight Python 3.11 image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy all UI files, including SDK folder, into container
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8502

# Run Streamlit UI
CMD ["streamlit","run","app.py","--server.port=8502","--server.address=0.0.0.0"]
