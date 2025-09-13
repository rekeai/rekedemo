# platform_api/app.py
import os, time, tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sdk.reke_sdk import verify_image_treering, verify_video_hybrid, embed_image_treering

BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

PRICE_PER_VERIFICATION = float(os.getenv("REKE_PRICE", "0.001"))

app = FastAPI(title="Reke Platform API (Demo)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

METRICS = {'total': 0, 'verified': 0, 'unverified': 0, 'last_10': []}

@app.get("/", response_class=FileResponse)
def home():
    # simple instructions page returned as text file for convenience
    content = ("Reke Platform API (Demo)\n\n"
               "POST files to /verify/ to check.\n"
               "GET /samples to see available demo files.\n"
               "GET /sample/{filename} to download a sample.\n")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp.write(content.encode()); tmp.close()
    return FileResponse(tmp.name, media_type="text/plain", filename="README.txt")

@app.post("/verify/")
async def verify_file(file: UploadFile = File(...)):
    content = await file.read()
    mime = (file.content_type or "").lower()

    try:
        if mime.startswith('video'):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp.write(content); tmp.close()
            status, manifest, sig_ok = verify_video_hybrid(tmp.name)
            try: os.unlink(tmp.name)
            except: pass
        else:
            status, manifest, sig_ok = verify_image_treering(content)
    except Exception as e:
        return JSONResponse({'status': 'Unknown', 'error': str(e)}, status_code=500)

    METRICS['total'] += 1
    if status == "AI Generated":
        METRICS['verified'] += 1
    else:
        METRICS['unverified'] += 1

    rec = {
        'filename': getattr(file, 'filename', 'uploaded'),
        'mime': mime,
        'status': status,
        'sig_valid': bool(sig_ok),
        'timestamp': time.time()
    }
    METRICS['last_10'].append(rec)
    METRICS['last_10'] = METRICS['last_10'][-10:]

    return JSONResponse({
        'status': status,
        'signature_valid': bool(sig_ok),
        'price': PRICE_PER_VERIFICATION,
        'manifest': manifest
    })

@app.get("/metrics")
def metrics():
    revenue = METRICS['total'] * PRICE_PER_VERIFICATION
    return {'metrics': METRICS, 'price_per_verification': PRICE_PER_VERIFICATION, 'estimated_revenue_this_session': revenue}

@app.get("/samples")
def list_samples():
    files = sorted(f for f in os.listdir(SAMPLES_DIR) if os.path.isfile(os.path.join(SAMPLES_DIR, f)))
    return {"samples": files}

@app.get("/sample/{filename}")
def sample_file(filename: str):
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse({'error': 'not found'}, status_code=404)
    mime = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    return FileResponse(path, media_type=mime, filename=filename)

@app.post("/sample/generate_ai")
def generate_ai():
    """
    Helper to create an AI watermarked sample from default_real.png.
    Not used by UI automatically — developer endpoint.
    """
    base = os.path.join(SAMPLES_DIR, "default_real.png")
    if not os.path.exists(base):
        return {"error": "default_real.png missing in samples"}
    out = os.path.join(SAMPLES_DIR, "ai_generated_sample.reke.png")
    embed_image_treering(base, out, origin="SampleAI")
    return {"created": out}
