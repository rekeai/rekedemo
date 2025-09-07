import os
import requests
import streamlit as st

# -------------------------
# Configuration
# -------------------------
API_URL = os.getenv('REKE_API_URL', 'http://localhost:8000')

st.set_page_config(
    page_title='Fake Platform • Reke Demo',
    page_icon='🛡️',
    layout='wide'
)

st.title('🛡️ Fake Platform (Toggle: Without API / With API)')

# -------------------------
# Layout: Columns
# -------------------------
left, right = st.columns([2, 1])

# ---------- LEFT COLUMN: Upload content ----------
with left:
    st.subheader('Upload content (simulate a user post)')

    # File uploader
    up = st.file_uploader(
        'Choose an image or short video (PNG/JPG/MP4)',
        type=['png', 'jpg', 'jpeg', 'mp4']
    )

    # Toggle platform mode
    mode = st.radio('Platform mode:', ('Without Reke API', 'With Reke API'))

    if up and st.button('Post'):
        if mode == 'Without Reke API':
            st.warning('❓ Unknown – platform has no verification integrated.')
        else:
            # Send the uploaded file to Platform API
            files = {'file': (up.name, up.getvalue(), up.type)}
            try:
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    data = r.json()
                    badge = 'Real' if data.get('status') == 'Real' else 'Fake'

                    # Display badge visually
                    if badge == 'Real':
                        st.success(f'✅ {badge} – Hidden watermark detected.')
                    else:
                        st.error(f'❌ {badge} – No hidden watermark found.')

                    # Show full API response
                    st.json(data)
                else:
                    st.error('API error – could not verify file.')
            except Exception as e:
                st.error(f'API call failed: {e}')

# ---------- RIGHT COLUMN: Demo & Metrics ----------
with right:
    # Demo video / Loom link
    st.subheader('Demo video (Loom)')
    st.markdown(
        'Shows full flow: AI generator → Reke SDK watermark → Platform toggle → Real/Fake badge.'
    )
    demo_link = st.text_input('Paste Loom demo URL (optional)', 'https://www.loom.com/share/your-demo-url')
    if demo_link and st.button('Open Loom Demo'):
        st.write('Open this in a new tab:', demo_link)

    # Session metrics
    st.subheader('Session metrics')
    try:
        metrics = requests.get(f"{API_URL}/metrics", timeout=5).json()
        st.metric('Total verifications', metrics['metrics']['total'])
        st.metric('Verified as Real', metrics['metrics']['verified'])
        st.metric('Verified as Fake', metrics['metrics']['unverified'])
        st.metric('Estimated revenue (session)', f"£{metrics['estimated_revenue_this_session']:.2f}")

        # Recent activity table
        st.write('Recent activity')
        st.table(metrics['metrics']['last_10'])
    except Exception:
        st.warning('API metrics not available. Make sure the Platform API service is running.')
