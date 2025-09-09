# fake_generator/app.py
import os, uuid
import streamlit as st
from PIL import Image, ImageDraw
from sdk.reke_sdk import embed_image_treering, embed_video_hybrid
import requests

REKE_API_URL = os.getenv("REKE_API_URL", "")
REKE_ORIGIN = os.getenv("REKE_ORIGIN", "Fake AI Generator")

st.title("Fake AI Generator (Demo)")

def generate_placeholder_image():
    img = Image.new('RGB', (512, 512), color=(200, 200, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Demo AI Image", fill=(0, 0, 0))
    path = f"temp_{uuid.uuid4().hex}.png"
    img.save(path)
    return path

if st.button("Create demo AI image"):
    img_path = generate_placeholder_image()
    output_path = embed_image_treering(img_path, f"{uuid.uuid4().hex}.reke.png", origin=REKE_ORIGIN)
    st.image(output_path)
    st.download_button("Download AI Image", output_path)

    if REKE_API_URL:
        with open(output_path, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{REKE_API_URL}/verify/", files=files)
            st.json(resp.json())
