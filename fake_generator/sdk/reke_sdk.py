# platform_api/sdk/reke_sdk.py  (COPY THIS IDENTICAL into fake_generator/sdk/reke_sdk.py)
"""
Reke demo SDK (images + hybrid video).
- Embeds a JSON manifest into PNG tEXt chunk.
- Adds a tiny LSB pattern into the red channel for demo detection (Tree-Ring-like simulation).
- Signs the content hash with HMAC(REKE_SECRET).
- Video: stamps selected frames and writes manifest into file metadata (ffmpeg).
Note: demo-only. Not production tamper-proof.
"""

import os, io, json, hashlib, hmac, subprocess, tempfile
from datetime import datetime, timezone
from PIL import Image, PngImagePlugin

REKE_SECRET = os.getenv("REKE_SECRET", "reke_demo_secret")
WATERMARK_MARK = "REKE-TR-DEMO"

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def _content_hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _hmac_sig(content_hash: str) -> str:
    return hmac.new(REKE_SECRET.encode(), content_hash.encode(), hashlib.sha256).hexdigest()

def _build_manifest(origin: str, content_hash: str) -> dict:
    return {
        "spec": "reke-demo-v1",
        "timestamp": _now_iso(),
        "origin": origin,
        "mark": WATERMARK_MARK,
        "content_hash": content_hash,
        "sig": _hmac_sig(content_hash)
    }

# ---------------- Image: embed & verify ----------------
def embed_image_treering(image_path: str, output_path: str, origin: str = "Fake AI Generator") -> str:
    """
    Embed a simple demo "tree-ring" (LSB + PNG tEXt manifest) into an image.
    Returns the path to the saved watermarked PNG.
    """
    img = Image.open(image_path).convert("RGBA")
    pixels = img.tobytes()
    content_hash = _content_hash_bytes(pixels)
    manifest = _build_manifest(origin, content_hash)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("reke_manifest", json.dumps(manifest))

    # pattern derived from HMAC - small demo LSB pattern
    sig = _hmac_sig(content_hash)
    pattern = bytes.fromhex(sig)[:64]  # demo bytes
    w, h = img.size
    px = img.load()
    idx = 0
    for y in range(min(h, 32)):
        for x in range(min(w, 32)):
            r, g, b, a = px[x, y]
            bit = (pattern[idx % len(pattern)] & 1)
            r = (r & ~1) | bit
            px[x, y] = (r, g, b, a)
            idx += 1

    base, ext = os.path.splitext(output_path)
    if ext.lower() != ".png":
        output_path = base + ".reke.png"
    img.save(output_path, "PNG", pnginfo=pnginfo, optimize=True)
    return output_path

def verify_image_treering(image_bytes: bytes):
    """
    Verify: returns tuple (status_str, manifest_or_none, sig_ok_bool)
    status_str is exactly "AI Generated" or "Real" or "Unknown"
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return "Unknown", None, False

    manifest = None
    sig_ok = False

    if img.format == "PNG":
        mstr = img.info.get("reke_manifest")
        if mstr:
            try:
                manifest = json.loads(mstr)
            except Exception:
                manifest = None
        if manifest and "content_hash" in manifest and "sig" in manifest:
            expected_sig = _hmac_sig(manifest["content_hash"])
            if expected_sig == manifest.get("sig"):
                # LSB sanity check (first bit)
                px = img.convert("RGBA").load()
                w, h = img.size
                bits = []
                for y in range(min(h, 32)):
                    for x in range(min(w, 32)):
                        r, g, b, a = px[x, y]
                        bits.append(r & 1)
                try:
                    expected_first_bit = int(expected_sig[0], 16) & 1
                    if bits and bits[0] == expected_first_bit:
                        sig_ok = True
                except Exception:
                    sig_ok = False
    else:
        # fallback: try comment field
        try:
            comment = img.info.get("comment", "")
            if comment.startswith("REKE_MANIFEST:"):
                manifest = json.loads(comment.split("REKE_MANIFEST:", 1)[1])
                sig_ok = (manifest.get("sig") == _hmac_sig(manifest.get("content_hash", "")))
        except Exception:
            manifest = None
            sig_ok = False

    if manifest and sig_ok:
        return "AI Generated", manifest, True
    else:
        return "Real", None, False

# ---------------- Video: embed & verify (demo) ----------------
def embed_video_hybrid(video_path: str, output_path: str, origin: str = "Fake AI Generator") -> str:
    """
    Demo hybrid: extract frames, stamp some frames, then copy metadata manifest into the video.
    Requires ffmpeg installed in the image.
    """
    with open(video_path, "rb") as f:
        vbytes = f.read()
    content_hash = _content_hash_bytes(vbytes)
    manifest = _build_manifest(origin, content_hash)

    import os
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        frames_pattern = os.path.join(tmp, "frame_%06d.png")
        cmd_extract = f'ffmpeg -y -i "{video_path}" -vf "select=not(mod(n\\,10))" -vsync vfr "{frames_pattern}"'
        subprocess.call(cmd_extract, shell=True)
        # stamp extracted frames
        for fn in sorted(os.listdir(tmp)):
            if fn.startswith("frame_") and fn.endswith(".png"):
                fp = os.path.join(tmp, fn)
                try:
                    embed_image_treering(fp, fp, origin=origin)
                except Exception:
                    pass
        # write manifest comment to output (best-effort demo)
        manifest_json = json.dumps(manifest).replace('"', '\\"')
        cmd_meta = f'ffmpeg -y -i "{video_path}" -metadata comment="{manifest_json}" -c copy "{output_path}"'
        code = subprocess.call(cmd_meta, shell=True)
        if code != 0:
            raise RuntimeError("ffmpeg failed to write metadata; ensure ffmpeg installed")
    return output_path

def verify_video_hybrid(video_path: str):
    """
    Read ffprobe metadata comment and validate HMAC. Returns same shape as image verify.
    """
    cmd = f'ffprobe -v quiet -print_format json -show_format "{video_path}"'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout:
        return "Unknown", None, False
    try:
        info = json.loads(p.stdout)
    except Exception:
        return "Unknown", None, False
    comment = info.get("format", {}).get("tags", {}).get("comment", "")
    if not comment:
        return "Real", None, False
    try:
        manifest = json.loads(comment)
    except Exception:
        return "Unknown", None, False
    sig_ok = (manifest.get("sig") == _hmac_sig(manifest.get("content_hash", "")))
    if manifest and sig_ok:
        return "AI Generated", manifest, True
    else:
        return "Real", None, False
