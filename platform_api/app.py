# platform_api/app.py
import os, time, tempfile, shutil, logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from sdk.reke_sdk import embed_image_treering, embed_video_hybrid, verify_image_treering, verify_video_hybrid

PRICE_PER_VERIFICATION = float(os.getenv("REKE_PRICE", "0.001"))
SAMPLES_DIR = "samples"
DEFAULT_REAL = "default_real.png"
os.makedirs(SAMPLES_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("reke-api")

app = FastAPI(title="Reke Platform API (Demo)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

METRICS = {"total": 0, "verified": 0, "unverified": 0, "last_10": []}

@app.get("/", response_class=HTMLResponse)
def home():
    return (
        "<html><body><h2>Reke Platform API (Demo)</h2>"
        "<p>Use POST /verify/ to verify a file. Example form below:</p>"
        '<form action="/verify/" enctype="multipart/form-data" method="post">'
        '<input name="file" type="file"/><input type="submit" value="Verify"/></form>'
        '<p><a href="/metrics">/metrics</a></p></body></html>'
    )

@app.post("/verify/")
async def verify_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="missing file")
    content = await file.read()
    mime = (file.content_type or "").lower()

    try:
        if mime.startswith("video"):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp.write(content); tmp.close()
            status, manifest, sig_ok = verify_video_hybrid(tmp.name)
            try: os.unlink(tmp.name)
            except Exception: pass
        else:
            status, manifest, sig_ok = verify_image_treering(content)
    except Exception as e:
        log.exception("verification error")
        return JSONResponse({"status": "Unknown", "error": str(e)}, status_code=500)

    METRICS["total"] += 1
    if status == "AI Generated":
        METRICS["verified"] += 1
    else:
        METRICS["unverified"] += 1

    rec = {"filename": file.filename, "mime": mime, "status": status, "sig_valid": bool(sig_ok), "timestamp": time.time()}
    METRICS["last_10"].append(rec)
    METRICS["last_10"] = METRICS["last_10"][-10:]

    return JSONResponse({"status": status, "signature_valid": bool(sig_ok), "price": PRICE_PER_VERIFICATION, "manifest": manifest})

@app.get("/metrics")
def metrics():
    revenue = METRICS["total"] * PRICE_PER_VERIFICATION
    return {"metrics": METRICS, "price_per_verification": PRICE_PER_VERIFICATION, "estimated_revenue_this_session": revenue}

@app.get("/sample/ai")
def sample_ai():
    path = os.path.join(SAMPLES_DIR, "sample_ai.reke.png")
    if not os.path.exists(path):
        # create default real placeholder if absent
        if not os.path.exists(DEFAULT_REAL):
            from PIL import Image, ImageDraw
            im = Image.new("RGB", (640, 480), (240, 240, 255))
            d = ImageDraw.Draw(im)
            d.text((10, 10), "Default real placeholder", fill=(0, 0, 0))
            im.save(DEFAULT_REAL)
        embed_image_treering(DEFAULT_REAL, path, origin="SampleAI")
    return FileResponse(path, media_type="image/png", filename="sample_ai.reke.png")

@app.get("/sample/real")
def sample_real():
    path = os.path.join(SAMPLES_DIR, "sample_real.png")
    if not os.path.exists(path):
        if not os.path.exists(DEFAULT_REAL):
            from PIL import Image, ImageDraw
            im = Image.new("RGB", (640, 480), (200, 240, 200))
            d = ImageDraw.Draw(im)
            d.text((10, 10), "Default real placeholder", fill=(0, 0, 0))
            im.save(DEFAULT_REAL)
        shutil.copy(DEFAULT_REAL, path)
    return FileResponse(path, media_type="image/png", filename="sample_real.png")
