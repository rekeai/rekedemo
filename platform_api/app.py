# platform_api/app.py
import os, time, tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from sdk.reke_sdk import (
    embed_image_treering,
    embed_video_hybrid,
    verify_image_treering,
    verify_video_hybrid
)

PRICE_PER_VERIFICATION = float(os.getenv("REKE_PRICE", "0.001"))

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
    <p>Sample endpoints: <a href="/sample/ai">/sample/ai</a> and <a href="/sample/real">/sample/real</a></p>
    <p><a href="/metrics">Metrics</a></p>
    </body></html>"""


@app.post('/verify/')
async def verify_file(file: UploadFile = File(...)):
    content = await file.read()
    mime = file.content_type or ''

    if mime.startswith('video'):
        tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        tmp.write(content)
        tmp.flush()
        tmp.close()
        status, manifest, sig_ok = verify_video_hybrid(tmp.name)
        try:
            os.remove(tmp.name)
        except Exception:
            pass
    else:
        status, manifest, sig_ok = verify_image_treering(content)

    METRICS['total'] += 1
    if status == "AI Generated":
        METRICS['verified'] += 1
    else:
        METRICS['unverified'] += 1

    rec = {
        'filename': file.filename,
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


@app.get('/metrics')
def metrics():
    revenue = METRICS['total'] * PRICE_PER_VERIFICATION
    return {
        'metrics': METRICS,
        'price_per_verification': PRICE_PER_VERIFICATION,
        'estimated_revenue_this_session': revenue
    }


# ----------------------
# Sample endpoints for demo UI
# ----------------------
@app.get('/sample/ai')
def sample_ai():
    """
    Dynamically build a demo AI image, embed the Reke watermark (using the SDK),
    and return it for download/use in the Platform UI.
    """
    # Build a simple demo image
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1024, 640), color=(40, 40, 80))
    d = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("DejaVuSans.ttf", 48)
    except Exception:
        fnt = None
    d.text((40, 260), "Demo AI image\n(embedded watermark)", fill=(255,255,255), font=fnt)

    tmp_in = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp_in_name = tmp_in.name
    img.save(tmp_in_name)
    tmp_in.close()

    out_path = tmp_in_name + '.reke.png'
    embed_image_treering(tmp_in_name, out_path, origin="Platform Sample AI")
    try:
        os.remove(tmp_in_name)
    except Exception:
        pass

    return FileResponse(out_path, media_type='image/png', filename='sample_ai.reke.png')


@app.get('/sample/real')
def sample_real():
    """
    Return a simple sample 'real' image (no watermark) for demonstration.
    """
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1024, 640), color=(220, 220, 230))
    d = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("DejaVuSans.ttf", 48)
    except Exception:
        fnt = None
    d.text((40, 260), "Demo Real image\n(no watermark)", fill=(20,20,20), font=fnt)

    tmp_in = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp_in_name = tmp_in.name
    img.save(tmp_in_name)
    tmp_in.close()

    return FileResponse(tmp_in_name, media_type='image/png', filename='sample_real.png')
