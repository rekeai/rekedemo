# Reke Demo — Investor Prototype

This repository contains an **investor-facing demo** of **Reke**, a watermark + verification system for AI-generated content.

## 🔹 Components

- **SDK (`sdk/reke_sdk.py`)**  
  - Demo Tree-Ring–style watermark for images.  
  - Hybrid video watermark: key-frame stamping + file-level manifest.  

- **Fake Generator (`fake_generator`)**  
  - Streamlit app that **always produces AI-generated watermarked content**.  
  - Download option and “Send to Platform” integration.

- **Platform API (`platform_api`)**  
  - FastAPI service to verify content.  
  - Endpoints:
    - `/verify/` → Verify an uploaded image or video.
    - `/sample/ai` → Download a demo AI-generated image (watermarked).
    - `/sample/real` → Download a demo “real” image (not watermarked).
    - `/metrics` → Session metrics & revenue estimate.

- **Platform UI (`platform_ui`)**  
  - Streamlit app for platforms.  
  - Upload toggle:
    - **Without API** → Blind, returns “Unknown.”  
    - **With API** → Detects “AI Generated” (if watermarked) or “Real” (if not).

- **Deployment**  
  - Dockerfiles in each service.  
  - `docker-compose.yml` for local testing.  
  - `render.yaml` for Render.com deployment.

---

## 🚀 Quick Start (Local with Docker Compose)

1. Install Docker & Docker Compose.  
2. From repo root:

   ```bash
   docker compose up --build
