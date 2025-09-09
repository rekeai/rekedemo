FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8000
ENV REKE_SECRET="reke_demo_secret" REKE_PRICE="0.001"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
