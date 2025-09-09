# platform_ui/app.py
import os, requests, streamlit as st

API_URL = os.getenv("REKE_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Fake Platform • Reke Demo", page_icon="🛡️", layout="wide")
st.title("🛡️ Fake Platform (Toggle: Without API / With API)")

left, right = st.columns([2,1])

def verify_bytes(bts, fname, mimetype):
    files = {"file": (fname, bts, mimetype)}
    r = requests.post(f"{API_URL}/verify/", files=files, timeout=30)
    return r

with left:
    st.subheader("Upload content (simulate a user post)")
    up = st.file_uploader("Choose image or video", type=["png","jpg","jpeg","mp4"])
    mode = st.radio("Platform mode:", ("Without Reke API", "With Reke API"))

    st.markdown("**Quick samples**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sample AI image (from API)"):
            try:
                r = requests.get(f"{API_URL}/sample/ai", timeout=10)
                if r.ok:
                    bts = r.content
                    if mode == "With Reke API":
                        resp = verify_bytes(bts, "sample_ai.reke.png", "image/png")
                        if resp.ok:
                            data = resp.json()
                            status = data.get("status")
                            if status == "AI Generated":
                                st.success("✅ AI Generated — Hidden watermark detected.")
                            else:
                                st.info("🟦 Real — No watermark found.")
                            st.download_button("Download sample AI", bts, file_name="sample_ai.reke.png", mime="image/png")
                        else:
                            st.error("API verification failed")
                    else:
                        st.warning("❓ Unknown — platform has no verification integrated.")
                        st.download_button("Download sample AI", bts, file_name="sample_ai.reke.png", mime="image/png")
                else:
                    st.error("Could not fetch sample from API")
            except Exception as e:
                st.error(f"Fetch error: {e}")
    with c2:
        if st.button("Sample Real image (from API)"):
            try:
                r = requests.get(f"{API_URL}/sample/real", timeout=10)
                if r.ok:
                    bts = r.content
                    if mode == "With Reke API":
                        resp = verify_bytes(bts, "sample_real.png", "image/png")
                        if resp.ok:
                            data = resp.json()
                            status = data.get("status")
                            if status == "AI Generated":
                                st.success("✅ AI Generated — Hidden watermark detected.")
                            else:
                                st.info("🟦 Real — No watermark found.")
                            st.download_button("Download sample Real", bts, file_name="sample_real.png", mime="image/png")
                        else:
                            st.error("API verification failed")
                    else:
                        st.warning("❓ Unknown — platform has no verification integrated.")
                        st.download_button("Download sample Real", bts, file_name="sample_real.png", mime="image/png")
                else:
                    st.error("Could not fetch sample from API")
            except Exception as e:
                st.error(f"Fetch error: {e}")

    st.markdown("---")
    if up and st.button("Post"):
        if mode == "Without Reke API":
            st.warning("❓ Unknown – platform has no verification integrated.")
        else:
            try:
                files = {"file": (up.name, up.getvalue(), up.type)}
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    data = r.json()
                    status = data.get("status")
                    if status == "AI Generated":
                        st.success("✅ AI Generated – Hidden watermark detected.")
                    elif status == "Real":
                        st.info("🟦 Real – No watermark found.")
                    else:
                        st.warning("❓ Unknown – Could not verify.")
                    if status == "AI Generated":
                        st.json(data)
                    st.download_button("Download posted file", up.getvalue(), file_name=up.name, mime=up.type)
                else:
                    st.error("API error – could not verify file.")
            except Exception as e:
                st.error(f"API call failed: {e}")

with right:
    st.subheader("Demo video (Loom)")
    st.markdown("A short Loom demo shows: generator → SDK → platform toggle → Real/Fake badge.")
    demo_link = st.text_input("Paste Loom demo URL (optional)", "https://www.loom.com/share/your-demo-url")
    if demo_link and st.button("Open Loom Demo"):
        st.write("Open this in a new tab:", demo_link)

    st.subheader("Session metrics")
    try:
        m = requests.get(f"{API_URL}/metrics", timeout=5).json()
        st.metric("Total verifications", m["metrics"]["total"])
        st.metric("AI Generated (verified)", m["metrics"]["ai_generated"])
        st.metric("Real / Unverified", m["metrics"]["real"])
        st.metric("Estimated revenue (session)", f"£{m['estimated_revenue_this_session']:.2f}")
        st.write("Recent activity")
        st.table(m["metrics"]["last_10"])
    except Exception:
        st.warning("API metrics not available. Start the API service first.")
