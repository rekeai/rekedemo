# platform_api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# minimal system deps (ffmpeg for video handling; lightweight display libs)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libglib2.0-0 libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
