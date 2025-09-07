import os, time
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sdk.reke_sdk import verify_image_treering, verify_video_hybrid

# Price per verification (from environment variable)
PRICE_PER_VERIFICATION = float(os.getenv("REKE_PRICE", "0.001"))

app = FastAPI(title="Reke Platform API (Demo)", description="Paid verification API")

# Allow cross-origin requests for demo purposes
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Simple in-memory metrics
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

@app.post('/verify/')
async def verify_file(file: UploadFile = File(...)):
    content = await file.read()
    mime = file.content_type or ''
    
    # Decide verification method based on file type
    if mime.startswith('video'):
        tmp = 'temp_upload.mp4'
        with open(tmp, 'wb') as f:
            f.write(content)
        ok, manifest, sig_ok = verify_video_hybrid(tmp)
    else:
        ok, manifest, sig_ok = verify_image_treering(content)
    
    # Update metrics
    METRICS['total'] += 1
    if ok:
        METRICS['verified'] += 1
        status = 'Real'
    else:
        METRICS['unverified'] += 1
        status = 'Fake'
    
    # Store last 10 uploads
    rec = {
        'filename': file.filename,
        'mime': mime,
        'status': status,
        'sig_valid': bool(sig_ok),
        'timestamp': time.time()
    }
    METRICS['last_10'].append(rec)
    METRICS['last_10'] = METRICS['last_10'][-10:]
    
    # Return verification result
    return JSONResponse({
        'status': status,
        'signature_valid': bool(sig_ok),
        'price': PRICE_PER_VERIFICATION,
        'manifest': manifest
    })

@app.get('/metrics')
def metrics():
    revenue = METRICS['total'] * PRICE_PER_VERIFICATION
    return {
        'metrics': METRICS,
        'price_per_verification': PRICE_PER_VERIFICATION,
        'estimated_revenue_this_session': revenue
    }
