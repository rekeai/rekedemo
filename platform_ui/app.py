# platform_ui/app.py
import os, requests
import streamlit as st
from PIL import Image

REKE_API_URL = os.getenv("REKE_API_URL", "")

st.title("Platform UI Demo (Fake vs Real Detection)")

use_api = st.checkbox("Use Reke API", value=True)
uploaded_files = st.file_uploader("Upload content (PNG/JPG/MP4)", accept_multiple_files=True)

# Quick Samples
st.subheader("Quick Samples")
col1, col2 = st.columns(2)
with col1:
    if st.button("Sample AI"):
        r = requests.get(f"{REKE_API_URL}/sample/ai")
        with open("sample_ai.reke.png", "wb") as f: f.write(r.content)
        st.image("sample_ai.reke.png", caption="Sample AI Image")
with col2:
    if st.button("Sample Real"):
        r = requests.get(f"{REKE_API_URL}/sample/real")
        with open("sample_real.png", "wb") as f: f.write(r.content)
        st.image("sample_real.png", caption="Sample Real Image")

# Uploaded files verification
if uploaded_files:
    for file in uploaded_files:
        img_bytes = file.read()
        if use_api:
            resp = requests.post(f"{REKE_API_URL}/verify/", files={"file": img_bytes})
            data = resp.json()
            if data.get("status") == "AI Generated":
                st.success(f"{file.name} → 🟥 AI Generated")
            else:
                st.info(f"{file.name} → 🟦 Real")
        else:
            st.info(f"{file.name} → 🟦 Real (API off)")
