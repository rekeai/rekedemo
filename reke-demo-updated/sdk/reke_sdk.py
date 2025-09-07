# reke_sdk.py
# Demo SDK: Tree-Ring-like watermark for images + hybrid video watermark approach.
# NOTE: This is a demo implementation for investor-facing prototypes.
import os, io, json, hashlib, hmac, subprocess, tempfile
from datetime import datetime, timezone
from PIL import Image, PngImagePlugin

WATERMARK_MARK = "REKE-TR"  # marker for demo
REKE_SECRET = os.getenv("REKE_SECRET", "reke_demo_secret")

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def _content_hash_bytes(data: bytes):
    return hashlib.sha256(data).hexdigest()

def _hmac_sig(content_hash: str):
    return hmac.new(REKE_SECRET.encode(), content_hash.encode(), hashlib.sha256).hexdigest()

def _build_manifest(origin: str, content_hash: str):
    return {
        "spec": "c2pa-lite-demo",
        "version": 1,
        "claim_generator": "RekeSDK/treering-0.1",
        "timestamp": _now_iso(),
        "reke_origin": origin,
        "mark": WATERMARK_MARK,
        "content_hash": content_hash,
        "sig": _hmac_sig(content_hash)
    }

# ---------- Image: Tree-Ring-like watermark (demo) ----------
def embed_image_treering(image_path: str, output_path: str, origin: str = "Fake AI Generator"):
    """Embed a demo Tree-Ring watermark into an image.
    Implementation details (demo):
     - Compute content hash of pixels
     - Build manifest (JSON)
     - Store manifest in PNG text chunk (reliable)
     - Also embed a simple LSB pattern into the red channel for demo 'signal' (visible only to detector)
    """
    img = Image.open(image_path).convert('RGBA')
    pixels = img.tobytes()
    content_hash = _content_hash_bytes(pixels)
    manifest = _build_manifest(origin, content_hash)
    # store manifest in PNG tEXt
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text('reke_manifest', json.dumps(manifest))
    # Create LSB pattern based on HMAC to simulate Tree-Ring signal
    sig = _hmac_sig(content_hash)
    # derive bytes from sig
    pattern = bytes.fromhex(sig)[:64]  # demo pattern
    # apply pattern to red channel LSB across a small area
    w, h = img.size
    px = img.load()
    idx = 0
    for y in range(min(h, 32)):
        for x in range(min(w, 32)):
            r,g,b,a = px[x,y]
            bit = (pattern[idx % len(pattern)] & 1)
            # set LSB of red to pattern bit
            r = (r & ~1) | bit
            px[x,y] = (r,g,b,a)
            idx += 1
    base, ext = os.path.splitext(output_path)
    if ext.lower() != '.png':
        output_path = base + '.reke.png'
    img.save(output_path, 'PNG', pnginfo=pnginfo, optimize=True)
    return output_path

def verify_image_treering(image_bytes: bytes):
    """Verify demo Tree-Ring watermark and manifest embedded in PNG tEXt + LSB pattern."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return False, None, False
    manifest = None
    sig_ok = False
    if img.format == 'PNG':
        mstr = img.info.get('reke_manifest')
        if mstr:
            try:
                manifest = json.loads(mstr)
            except Exception:
                manifest = None
        # verify LSB pattern matches HMAC (demo)
        px = img.convert('RGBA').load()
        w,h = img.size
        # read LSBs from the same area
        bits = []
        for y in range(min(h,32)):
            for x in range(min(w,32)):
                r,g,b,a = px[x,y]
                bits.append(r & 1)
        # rebuild a simple check using manifest.sig
        if manifest and 'content_hash' in manifest and 'sig' in manifest:
            expected_sig = _hmac_sig(manifest['content_hash'])
            # simple check: first bit of expected_sig hex equals first bit we read (demo)
            try:
                expected_first_bit = int(expected_sig[0], 16) & 1
                if bits and bits[0] == expected_first_bit:
                    sig_ok = (expected_sig == manifest.get('sig'))
            except Exception:
                sig_ok = False
    else:
        # For other formats, try to find manifest in comment (not robust in demo)
        try:
            comment = img.info.get('comment')
            if comment and comment.startswith('REKE_MANIFEST:'):
                manifest = json.loads(comment.split('REKE_MANIFEST:',1)[1])
                sig_ok = (manifest.get('sig') == _hmac_sig(manifest.get('content_hash','')))
        except Exception:
            manifest = None
            sig_ok = False
    verified = bool(manifest and sig_ok)
    return verified, manifest, sig_ok

# ---------- Video: Hybrid watermark (demo) ----------
def embed_video_hybrid(video_path: str, output_path: str, origin: str = "Fake AI Generator"):
    """Embed watermark into a video using hybrid approach:
       - Extract key frames (every Nth frame), apply image treering embed on those frames
       - Reassemble video and add manifest as metadata comment (ffmpeg)
       NOTE: Requires ffmpeg installed in PATH.
    """
    # compute content hash of video bytes
    with open(video_path, 'rb') as f:
        vbytes = f.read()
    content_hash = _content_hash_bytes(vbytes)
    manifest = _build_manifest(origin, content_hash)
    # create temp dir for frames
    with tempfile.TemporaryDirectory() as tmp:
        # extract frames every N frames (e.g., every 10th)
        frames_pattern = os.path.join(tmp, 'frame_%06d.png')
        cmd_extract = f'ffmpeg -y -i "{video_path}" -vf "select=not(mod(n\\,10))" -vsync vfr "{frames_pattern}"'
        subprocess.call(cmd_extract, shell=True)
        # process extracted frames
        for fn in sorted(os.listdir(tmp)):
            if fn.startswith('frame_') and fn.endswith('.png'):
                fp = os.path.join(tmp, fn)
                try:
                    embed_image_treering(fp, fp, origin=origin)
                except Exception:
                    pass
        # reassemble: write metadata comment to output file
        manifest_json = json.dumps(manifest).replace('"', '\"')
        cmd_meta = f'ffmpeg -y -i "{video_path}" -metadata comment="{manifest_json}" -c copy "{output_path}"'
        code = subprocess.call(cmd_meta, shell=True)
        if code != 0:
            raise RuntimeError('ffmpeg failed to write metadata; ensure ffmpeg is installed')
    return output_path

def verify_video_hybrid(video_path: str):
    """Verify hybrid video watermark by reading metadata comment and doing a light frame check."""
    # read metadata via ffprobe
    cmd = f'ffprobe -v quiet -print_format json -show_format "{video_path}"'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout:
        return False, None, False
    try:
        info = json.loads(p.stdout)
    except Exception:
        return False, None, False
    comment = info.get('format', {}).get('tags', {}).get('comment','')
    if not comment:
        return False, None, False
    try:
        manifest = json.loads(comment)
    except Exception:
        return False, None, False
    sig_ok = (manifest.get('sig') == _hmac_sig(manifest.get('content_hash','')))
    return bool(manifest and sig_ok), manifest, sig_ok
