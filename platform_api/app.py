# platform_api/app.py
import os, time, io, shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from sdk.reke_sdk import embed_image_treering, embed_video_hybrid, verify_image_treering, verify_video_hybrid

PRICE_PER_VERIFICATION = float(os.getenv("REKE_PRICE", "0.001"))
SAMPLES_DIR = "samples"
os.makedirs(SAMPLES_DIR, exist_ok=True)

app = FastAPI(title="Reke Platform API (Demo)", description="Paid verification API")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

METRICS = {'total': 0, 'verified': 0, 'unverified': 0, 'last_10': []}

@app.get('/', response_class=HTMLResponse)
def home():
    return """<html><body>
    <h2>Reke Platform API (Demo)</h2>
    <p>POST a file to /verify/ to test. Use the demo UI or this simple form:</p>
    <form action="/verify/" enctype="multipart/form-data" method="post">
    <input name="file" type="file"/><input type="submit" value="Verify"/>
    </form>
    <p><a href="/metrics">Metrics</a></p>
    </body></html>"""

# ---------------- Verification ----------------
@app.post('/verify/')
async def verify_file(file: UploadFile = File(...)):
    content = await file.read()
    mime = file.content_type or ''
    if mime.startswith('video'):
        tmp = 'temp_upload.mp4'
        with open(tmp, 'wb') as f:
            f.write(content)
        status, manifest, sig_ok = verify_video_hybrid(tmp)
        try: os.remove(tmp)
        except Exception: pass
    else:
        status, manifest, sig_ok = verify_image_treering(content)

    # Update metrics
    METRICS['total'] += 1
    if status == "AI Generated":
        METRICS['verified'] += 1
    else:
        METRICS['unverified'] += 1

    rec = {'filename': file.filename, 'mime': mime, 'status': status, 'sig_valid': bool(sig_ok), 'timestamp': time.time()}
    METRICS['last_10'].append(rec)
    METRICS['last_10'] = METRICS['last_10'][-10:]

    return JSONResponse({'status': status, 'signature_valid': bool(sig_ok), 'price': PRICE_PER_VERIFICATION, 'manifest': manifest})

# ---------------- Metrics ----------------
@app.get('/metrics')
def metrics():
    revenue = METRICS['total'] * PRICE_PER_VERIFICATION
    return {'metrics': METRICS, 'price_per_verification': PRICE_PER_VERIFICATION, 'estimated_revenue_this_session': revenue}

# ---------------- Sample Endpoints ----------------
@app.get("/sample/ai")
def sample_ai():
    path = os.path.join(SAMPLES_DIR, "sample_ai.reke.png")
    if not os.path.exists(path):
        # create watermarked AI sample
        embed_image_treering("default_real.png", path, origin="Fake AI Generator")
    return FileResponse(path, media_type="image/png", filename="sample_ai.reke.png")

@app.get("/sample/real")
def sample_real():
    path = os.path.join(SAMPLES_DIR, "sample_real.png")
    if not os.path.exists(path):
        shutil.copy("default_real.png", path)
    return FileResponse(path, media_type="image/png", filename="sample_real.png")
