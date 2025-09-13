# Reke Demo — Investor Prototype (Tree-Ring + Hybrid Video)

This repository contains an investor-facing demo of **Reke**:
- Free SDK (demo) that embeds an invisible watermark + simple origin manifest for images.
- Platform API (FastAPI) that verifies uploaded files and returns `AI Generated` / `Real`.
- Fake Generator (script) that can create an AI watermarked sample.
- Platform UI (Streamlit) with a polished gallery of sample images (no user upload) to demo behavior.

## Quick local run with Docker Compose

1. Add your sample images to `platform_api/samples/` with these filenames:
   - `real_dog.jpg`
   - `real_cat.jpg`
   - `real_child.jpg`
   - `real_man.jpg`
   - `real_woman.jpg`
   - `ai_portrait.png`
   - `ai_panda_chimp.png`
   - `ai_model.png`

2. Build & run:
Open the UI: http://localhost:8502

Click a sample (Real or AI).

Toggle With Reke API to see the platform call /verify/.

AI watermarked samples will show AI Generated — Watermark Found and downloads disabled.

Real samples will show Real — No watermark found and allow download.

Deploy on Render.com

Push repo to GitHub.

Create three services on Render (or use render.yaml):

reke-platform-api (Docker, root platform_api)

reke-platform-ui (Docker, root platform_ui)

reke-fake-generator (worker or web)

Deploy reke-platform-api first. Add environment variable:

REKE_SECRET (choose a long random value for demo)

After API is live, set REKE_API_URL on reke-platform-ui to the API URL.

Redeploy UI.

Notes

This is a demo/prototype. The watermark approach is a simplified Tree-Ring–like method for illustration.

For any problems check service logs (Render live tail) for errors.

---

## Final testing checklist (do these exactly)

1. Put images in `platform_api/samples/` with filenames above.
2. Run locally:
   - `docker compose up --build`
3. Visit `http://localhost:8502`:
   - Click one of **AI** images (ai_*). Toggle **With Reke API** => should show **AI Generated — Watermark Found**.
   - Click one of **Real** images (real_*) with API ON => should show **Real — No watermark found** and allow download.
   - Switch to **Without Reke API** => shows **Unknown** for any image.

If something returns “Real” for an AI sample, common causes:
- The AI sample you added is not a watermarked PNG produced by the SDK. (Make sure `ai_*.png` is an image created by `embed_image_treering` or the fake generator.)
- `REKE_SECRET` mismatched between where the sample was embedded and the API verification (HMAC will fail). For local Docker Compose, we used the same `REKE_SECRET` default in compose. On Render set the same `REKE_SECRET` for any service that may embed.

---

If you want I will:
- (A) produce a single downloadable zip containing every file and directory exactly as above ready for upload to GitHub, **or**
- (B) paste exact GitHub web UI clicks (step-by-step) to create the files directly in your repository, file by file, and then show the Render click-by-click deploy steps.

Which next? (Say `Zip please` or `Show GitHub steps` and I’ll do it right away.)
```bash
docker compose up --build
