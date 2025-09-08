# platform_ui/app.py
import os, requests, streamlit as st

API_URL = os.getenv("REKE_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Fake Platform • Reke Demo", page_icon="🛡️", layout="wide")
st.title("🛡️ Fake Platform (with/without Reke API)")

left, right = st.columns([2, 1])

with left:
    st.subheader("Upload content (simulate a user post)")
    up = st.file_uploader("Choose image/video", type=["png", "jpg", "jpeg", "mp4"])
    mode = st.radio("Platform mode:", ("Without Reke API", "With Reke API"))

    if up and st.button("Post"):
        if mode == "Without Reke API":
            st.warning("❓ Unknown – no verification available (platform blind).")
        else:
            files = {"file": (up.name, up.getvalue(), up.type)}
            try:
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    data = r.json()
                    status = data.get("status", "Unknown")
                    if status == "AI Generated":
                        st.error("❌ AI Generated – Hidden watermark detected.")
                    elif status == "Real":
                        st.success("✅ Real – No watermark found.")
                    else:
                        st.warning("❓ Unknown – Could not verify.")
                    st.json(data)
                else:
                    st.error("API error")
            except Exception as e:
                st.error(f"API call failed: {e}")

    st.markdown("---")
    st.subheader("📂 Or try a sample AI-generated file")
    if st.button("Use Sample AI Image"):
        sample = "sample_ai.reke.png"
        if os.path.exists(sample):
            with open(sample, "rb") as f:
                files = {"file": (sample, f.read(), "image/png")}
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    data = r.json()
                    st.error("❌ AI Generated – Verified via SDK")
                    st.json(data)
        else:
            st.warning("Sample file missing.")

with right:
    st.subheader("📊 Session metrics")
    try:
        m = requests.get(f"{API_URL}/metrics", timeout=5).json()
        st.metric("Total verifications", m["metrics"]["total"])
        st.metric("AI Generated", m["metrics"]["ai_generated"])
        st.metric("Real", m["metrics"]["real"])
        st.metric("Revenue (session)", f"£{m['estimated_revenue_this_session']:.2f}")
        st.table(m["metrics"]["last_10"])
    except Exception:
        st.warning("API metrics not available (start API service first).")
