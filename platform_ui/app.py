# platform_ui/app.py
import streamlit as st, requests, io
from PIL import Image

API_BASE = st.secrets.get("REKE_API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Reke Platform Demo", page_icon="🛡️", layout="wide")
st.title("🛡️ Reke Platform Demo — Sample Gallery")
st.caption("Select a sample image below. Toggle the API to see the platform response.")

mode = st.radio("Platform mode:", ["Without Reke API", "With Reke API"], horizontal=True)

# fetch samples list
try:
    resp = requests.get(f"{API_BASE}/samples", timeout=5)
    all_samples = resp.json().get("samples", [])
except Exception:
    all_samples = []

# Separate into Real vs AI by filename heuristic
real_list = [fn for fn in all_samples if fn.lower().startswith("real")]
ai_list = [fn for fn in all_samples if fn.lower().startswith("ai") or "ai_" in fn.lower() or ".reke" in fn.lower()]
# fallback: anything remaining -> real
others = [fn for fn in all_samples if fn not in real_list and fn not in ai_list]
real_list += others

def show_gallery(title, items):
    st.subheader(title)
    cols = st.columns(4)
    for idx, fn in enumerate(items):
        with cols[idx % 4]:
            try:
                r = requests.get(f"{API_BASE}/sample/{fn}", timeout=5)
                img = Image.open(io.BytesIO(r.content))
                if st.button(fn, key=title + "_" + fn):
                    st.session_state['selected'] = fn
                st.image(img, caption=fn, use_column_width=True)
            except Exception:
                st.write("Error loading", fn)

if real_list:
    show_gallery("Real Samples", real_list)
if ai_list:
    show_gallery("AI Samples", ai_list)

st.markdown("---")
sel = st.session_state.get('selected')
if sel:
    st.header("Selected: " + sel)
    r = requests.get(f"{API_BASE}/sample/{sel}", timeout=5)
    img_bytes = r.content
    st.image(img_bytes, use_column_width=True)
    if mode == "Without Reke API":
        st.warning("❓ Unknown — platform has no verification integrated.")
    else:
        # Call verify endpoint
        files = {'file': (sel, img_bytes, 'image/png' if sel.lower().endswith('.png') else 'image/jpeg')}
        try:
            res = requests.post(f"{API_BASE}/verify/", files=files, timeout=10)
            if res.ok:
                data = res.json()
                status = data.get('status', 'Unknown')
                if status == "AI Generated":
                    st.error("🟥 AI Generated — Watermark Found")
                    st.json(data)
                    st.warning("Download & browse disabled for AI-generated content.")
                elif status == "Real":
                    st.success("🟦 Real — No watermark found")
                    st.json(data)
                    st.download_button("⬇️ Download image", data=img_bytes, file_name=sel, mime='image/png' if sel.lower().endswith('.png') else 'image/jpeg')
                else:
                    st.info("❓ " + status); st.json(data)
            else:
                st.error("API error: " + str(res.status_code))
        except Exception as e:
            st.error("Verification failed: " + str(e))
else:
    st.info("Choose a sample above to inspect.")
