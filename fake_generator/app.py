# fake_generator/app.py
import os
from sdk.reke_sdk import embed_image_treering
from PIL import Image, ImageDraw

OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)

def make_demo_base(path):
    img = Image.new("RGB", (800,600), color=(245,245,255))
    d = ImageDraw.Draw(img)
    d.text((30,30), "REKE Fake Generator sample", fill=(10,10,10))
    img.save(path)

if __name__ == "__main__":
    base = os.path.join(OUT_DIR, "base.png")
    make_demo_base(base)
    out = os.path.join(OUT_DIR, "ai_sample.reke.png")
    embed_image_treering(base, out, origin="FakeGenerator")
    print("Created", out)
