# Reke Demo — Updated (Tree-Ring + Hybrid Video)

This repo contains an investor-facing demo of Reke. It includes:
- SDK with a Tree-Ring-style watermark for images (demo implementation)
- Hybrid watermark for videos: key-frame stamping + file-level manifest
- Fake AI Generator (Streamlit) that embeds watermark when "generating" content
- Platform API (FastAPI) that verifies files and returns Real / Fake
- Platform UI (Streamlit) with toggle (Without API / With API) and Loom demo placeholder
- Dockerfiles, docker-compose, and render.yaml for cloud deployment (Render.com)

Quick start (Docker):
1. Install Docker & Docker Compose
2. From repo root:
   docker compose up --build
3. Open:
   - API: http://localhost:8000
   - Fake Generator: http://localhost:8501
   - Platform UI: http://localhost:8502

Notes:
- This is a demo. A production Tree-Ring watermarking implementation is more advanced; here we simulate the idea using a manifest + a small LSB pattern.
- Video hybrid uses ffmpeg to attach a manifest and stamp selected frames; ffmpeg is required in the Docker images.
- Change REKE_SECRET in production; default demo secret is 'reke_demo_secret'.
