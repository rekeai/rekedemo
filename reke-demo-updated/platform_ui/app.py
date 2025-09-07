import os, requests, streamlit as st

API_URL = os.getenv('REKE_API_URL','http://localhost:8000')
st.set_page_config(page_title='Fake Platform • Reke Demo', page_icon='🛡️', layout='wide')
st.title('🛡️ Fake Platform (Toggle: Without API / With API)')

left, right = st.columns([2,1])
with left:
    st.subheader('Upload content (simulate a user post)')
    up = st.file_uploader('Choose an image or short video', type=['png','jpg','jpeg','mp4'])
    mode = st.radio('Platform mode:', ('Without Reke API','With Reke API'))
    if up and st.button('Post'):
        if mode == 'Without Reke API':
            st.warning('❓ Unknown – platform has no verification integrated.')
        else:
            files = {'file':(up.name, up.getvalue(), up.type)}
            try:
                r = requests.post(f"{API_URL}/verify/", files=files, timeout=60)
                if r.ok:
                    data = r.json()
                    badge = 'Real' if data.get('status')=='Real' else 'Fake'
                    if badge == 'Real':
                        st.success(f'✅ {badge} – AI generator detected.')
                    else:
                        st.error(f'❌ {badge} – No hidden watermark found.')
                    st.json(data)
                else:
                    st.error('API error')
            except Exception as e:
                st.error(f'API call failed: {e}')

with right:
    st.subheader('Demo video (Loom)')
    st.markdown('A short Loom demo shows: generator → SDK → platform toggle → Real/Fake badge.')
    demo_link = st.text_input('Paste Loom demo URL (optional)', 'https://www.loom.com/share/your-demo-url')
    if demo_link and st.button('Open Loom Demo'):
        st.write('Open this in a new tab:', demo_link)
    st.subheader('Session metrics')
    try:
        m = requests.get(f"{API_URL}/metrics", timeout=5).json()
        st.metric('Total verifications', m['metrics']['total'])
        st.metric('Real', m['metrics']['verified'])
        st.metric('Fake', m['metrics']['unverified'])
        st.metric('Estimated revenue (session)', f"£{m['estimated_revenue_this_session']:.2f}")
        st.write('Recent activity')
        st.table(m['metrics']['last_10'])
    except Exception:
        st.warning('API metrics not available. Start the API service first.')
