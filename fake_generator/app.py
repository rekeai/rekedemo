# fake_generator/app.py
import os, requests, streamlit as st
from sdk.reke_sdk import embed_image_treering, embed_video_hybrid

API_URL = os.getenv("REKE_API_URL", "http://localhost:8000")
ORIGIN = os.getenv("REKE_ORIGIN", "Fake AI Generator")

st.set_page_config(page_title="Fake AI Generator • Reke SDK", page_icon="🤖", layout="wide")
st.title("🤖 Fake AI Generator (with Reke SDK)")

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Upload image/video to simulate AI generation (always watermarked)")
    up = st.file_uploader("Upload file (png/jpg/mp4)", type=["png","jpg","jpeg","mp4"])
    if "generated" not in st.session_state:
        st.session_state["generated"] = None

    # Create a demo generated image (watermarked)
    if st.button("Create demo AI image (watermarked)"):
        # simple synthetic image
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1024, 640), color=(30,30,60))
        d = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype("DejaVuSans.ttf", 48)
        except Exception:
            fnt = None
        d.text((50,260), "AI sample image\n(embedded watermark)", fill=(255,255,255), font=fnt)
        tmp = "demo_ai.png"
        img.save(tmp)
        out = "demo_ai.reke.png"
        outp = embed_image_treering(tmp, out, origin=ORIGIN)
        st.image(outp, caption="AI Generated image (watermarked)", use_column_width=True)
        st.success("Hidden watermark embedded via Reke SDK ✅")
        st.session_state["generated"] = outp
        with open(outp,"rb") as f:
            st.download_button("⬇️ Download AI image", f.read(), file_name=os.path.basename(outp), mime="image/png")

    # Upload a file and embed watermark
    if up and st.button("Generate (embed Reke watermark)"):
        tmp = f"temp_{up.name}"
        with open(tmp,"wb") as f:
            f.write(up.getvalue())
        if up.type.startswith("image"):
            out = tmp + ".reke.png"
            outp = embed_image_treering(tmp, out, origin=ORIGIN)
            st.image(outp, caption="Generated image (watermarked)", use_column_width=True)
        else:
            out = tmp + ".reke.mp4"
            outp = embed_video_hybrid(tmp, out, origin=ORIGIN)
            st.video(outp)
        st.success("Hidden watermark embedded via Reke SDK ✅")
        st.session_state["generated"] = outp
        with open(outp,"rb") as f:
            st.download_button("⬇️ Download Generated File", f.read(), file_name=os.path.basename(outp))

with col2:
    st.subheader("Send to Platform API")
    gen = st.session_state.get("generated")
    if gen:
        st.write(f"Prepared: `{gen}`")
        if st.button("Send to Platform API → Verify"):
            with open(gen,"rb") as f:
                data = f.read()
            mime = "video/mp4" if gen.lower().endswith(".mp4") else "image/png"
            files = {"file": (os.path.basename(gen), data, mime)}
            try:
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    resp = r.json()
                    status = resp.get("status")
                    if status == "AI Generated":
                        st.success(f"✅ {status} — hidden watermark detected.")
                        st.json(resp)
                    elif status == "Real":
                        st.info(f"🟦 {status} — no hidden watermark found.")
                    else:
                        st.warning(f"❓ {status}")
                else:
                    st.error("API error")
            except Exception as e:
                st.error(f"API call failed: {e}")
    else:
        st.info("Generate something first on the left.")
