# platform_api/app.py
import os, io, uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sdk.reke_sdk import verify_image_treering, verify_video_hybrid, embed_image_treering
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="Reke Platform API", version="1.0")

# In-memory metrics
METRICS = {
    "total": 0,
    "ai_generated": 0,
    "real": 0,
    "last_10": [],
}
REKE_PRICE = float(os.getenv("REKE_PRICE", "0.001"))

# --- Verify endpoint ---
@app.post("/verify/")
async def verify(file: UploadFile = File(...)):
    try:
        if file.content_type.startswith("image/"):
            img_bytes = await file.read()
            status, manifest, sig_ok = verify_image_treering(img_bytes)
        elif file.content_type.startswith("video/"):
            tmp = f"/tmp/{uuid.uuid4()}_{file.filename}"
            with open(tmp, "wb") as f:
                f.write(await file.read())
            status, manifest, sig_ok = verify_video_hybrid(tmp)
        else:
            return JSONResponse({"status": "Unknown", "error": "Unsupported type"})

        # Update metrics
        METRICS["total"] += 1
        if status == "AI Generated":
            METRICS["ai_generated"] += 1
        elif status == "Real":
            METRICS["real"] += 1
        METRICS["last_10"].insert(0, {"status": status, "file": file.filename})
        METRICS["last_10"] = METRICS["last_10"][:10]

        return {"status": status, "manifest": manifest, "signature_ok": sig_ok}

    except Exception as e:
        return JSONResponse({"status": "Unknown", "error": str(e)})

# --- Metrics endpoint ---
@app.get("/metrics")
def metrics():
    revenue = METRICS["total"] * REKE_PRICE
    return {"metrics": METRICS, "estimated_revenue_this_session": revenue}

# --- Sample AI image (watermarked) ---
@app.get("/sample/ai")
def sample_ai():
    img = Image.new("RGB", (600, 400), color=(40, 40, 90))
    d = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("DejaVuSans.ttf", 32)
    except Exception:
        fnt = None
    d.text((40, 160), "AI Generated Sample", fill=(255, 255, 255), font=fnt)

    tmp = "/tmp/sample_ai.png"
    img.save(tmp)
    out = "/tmp/sample_ai.reke.png"
    embed_image_treering(tmp, out, origin="Sample AI Generator")

    with open(out, "rb") as f:
        return StreamingResponse(io.BytesIO(f.read()), media_type="image/png")

# --- Sample Real image (no watermark) ---
@app.get("/sample/real")
def sample_real():
    img = Image.new("RGB", (600, 400), color=(200, 220, 200))
    d = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("DejaVuSans.ttf", 32)
    except Exception:
        fnt = None
    d.text((40, 160), "Real Sample Image", fill=(0, 0, 0), font=fnt)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/")
def root():
    return {"message": "Reke Platform API is running", "endpoints": ["/verify/", "/metrics", "/sample/ai", "/sample/real"]}
