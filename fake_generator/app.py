# fake_generator/app.py
import os, streamlit as st
from sdk.reke_sdk import embed_image_treering, embed_video_hybrid

ORIGIN = os.getenv("REKE_ORIGIN", "Fake AI Generator")

st.set_page_config(page_title="Fake AI Generator • Reke SDK", page_icon="🤖", layout="wide")
st.title("🤖 Fake AI Generator (with Reke SDK)")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Upload image/video to simulate AI generation")
    up = st.file_uploader("Upload file", type=["png", "jpg", "jpeg", "mp4"])
    if "generated" not in st.session_state:
        st.session_state["generated"] = None

    if up and st.button("Generate (embed hidden Reke watermark)"):
        tmp = f"temp_{up.name}"
        with open(tmp, "wb") as f:
            f.write(up.getvalue())
        if up.type.startswith("image"):
            out = tmp + ".reke.png"
            outp = embed_image_treering(tmp, out, origin=ORIGIN)
            st.image(outp, caption="AI Generated image (watermarked)", use_column_width=True)
        else:
            out = tmp + ".reke.mp4"
            outp = embed_video_hybrid(tmp, out, origin=ORIGIN)
            st.video(outp)

        st.success("✅ Hidden watermark embedded via Reke SDK")
        st.session_state["generated"] = outp

        with open(outp, "rb") as f:
            st.download_button("⬇️ Download Generated File", f, file_name=os.path.basename(outp))

with col2:
    st.info("Watermark is invisible but verifiable.\n\nDownload your generated content, then upload it on the Fake Platform demo.")
