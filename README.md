# Reke Demo — Investor Prototype

This repo contains a demo of Reke: SDK + API + Platform UI to show AI image/video watermarking & instant verification.

## Structure
- `platform_api/` — FastAPI verification API + SDK copy
- `fake_generator/` — Streamlit demo generator that ALWAYS watermarks generated content (demo SDK)
- `platform_ui/` — Streamlit demo platform (toggle: Without API / With API)
- `docker-compose.yml` & `render.yaml` for deployment

## Quick local start (Docker)
1. Docker & Docker Compose installed.
2. From repo root: `docker compose up --build`
3. Open:
   - API: http://localhost:8000
   - Fake Generator: http://localhost:8501
   - Platform UI: http://localhost:8502

## Render deployment (high level)
1. Push code to GitHub.
2. Connect repo to Render and import the `render.yaml`.
3. Deploy `reke-platform-api` first.
4. In Render: set `REKE_SECRET` (same value for api & generator). Set `REKE_PRICE`.
5. Deploy generator & UI after setting `REKE_API_URL` to API public URL and `REKE_SECRET` for generator.
6. Test end-to-end.

## Demo flow for investors
1. Fake Generator → Create demo AI image (watermarked) → Download.
2. Platform UI → With API → Upload downloaded image → shows **AI Generated**.
3. Platform UI → Without API → Upload same image → shows **Unknown**.
4. Upload a non-watermarked image → With API → shows **Real**.

## Notes
- Ensure `REKE_SECRET` is same across API & generator, otherwise verification fails.
- The demo uses a simple manifest + LSB pattern; it is designed for investor demos, not as production cryptographic proof.

