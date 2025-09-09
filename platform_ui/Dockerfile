FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8502
ENV REKE_API_URL="http://localhost:8000"
CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]
