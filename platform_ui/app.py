# platform_ui/app.py
import os, requests, streamlit as st, uuid

REKE_API_URL = os.getenv("REKE_API_URL", "").rstrip("/")

st.set_page_config(page_title="Fake Platform • Reke Demo", page_icon="🛡️", layout="wide")
st.title("🛡️ Fake Platform (Toggle: Without API / With API)")

left, right = st.columns([2, 1])
with left:
    st.subheader("Upload content (simulate a user post)")
    uploaded = st.file_uploader("Choose an image or short video", type=["png", "jpg", "jpeg", "mp4"])
    mode = st.radio("Platform mode:", ("Without Reke API", "With Reke API"))

    if uploaded and st.button("Post"):
        if mode == "Without Reke API":
            st.warning("❓ Unknown – platform has no verification integrated.")
        else:
            tmp = f"/tmp/{uuid.uuid4().hex}_{uploaded.name}"
            with open(tmp, "wb") as f:
                f.write(uploaded.getvalue())
            try:
                with open(tmp, "rb") as f:
                    r = requests.post(f"{REKE_API_URL}/verify/", files={"file": (uploaded.name, f, uploaded.type)}, timeout=20)
                if r.ok:
                    data = r.json()
                    status = data.get("status", "Unknown")
                    if status == "AI Generated":
                        st.success(f"✅ {status} – Hidden watermark detected.")
                    elif status == "Real":
                        st.info(f"🟦 {status} – No watermark found.")
                    else:
                        st.warning(f"❓ {status}")
                    st.json(data)
                else:
                    st.error("API error: " + str(r.status_code))
            except Exception as e:
                st.error(f"API call failed: {e}")
            finally:
                try:
                    os.remove(tmp)
                except Exception:
                    pass

with right:
    st.subheader("Quick samples")
    if st.button("Download Sample AI (watermarked)"):
        try:
            r = requests.get(f"{REKE_API_URL}/sample/ai", timeout=10)
            open("sample_ai.reke.png", "wb").write(r.content)
            st.image("sample_ai.reke.png", caption="Sample AI (watermarked)")
        except Exception as e:
            st.error(f"Sample AI fetch failed: {e}")

    if st.button("Download Sample Real"):
        try:
            r = requests.get(f"{REKE_API_URL}/sample/real", timeout=10)
            open("sample_real.png", "wb").write(r.content)
            st.image("sample_real.png", caption="Sample Real (plain)")
        except Exception as e:
            st.error(f"Sample real fetch failed: {e}")

    st.subheader("Session metrics")
    try:
        m = requests.get(f"{REKE_API_URL}/metrics", timeout=5).json()
        st.metric("Total verifications", m["metrics"]["total"])
        st.metric("AI Generated", m["metrics"]["verified"])
        st.metric("Real", m["metrics"]["unverified"])
    except Exception:
        st.warning("API metrics not available. Start the API service first.")
