import streamlit as st

def render():
    # — CSS 정의: 카드 스타일 + 버튼 커스터마이징
    st.markdown("""
    <style>
      .option-card {
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        text-align: center;
      }
      .option-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        color: #3b63c4;
        text-align: center;
        
      }
      .stButton>button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: bold;
        border-radius: 0.5rem;
        border: none;
      }
      /* 카메라 버튼 */
      .stButton>button[data-testid="stButton"] {
        background-color: #2d9cdb;
        color: white;
      }
      .stButton>button[data-testid="stButton"]:hover {
        background-color: #2378a8;
      }
      /* 이미지 업로드 버튼 */
      .stButton>button[data-testid="stButton"+1] {
        background-color: #f39c12;
        color: white;
      }
      .stButton>button[data-testid="stButton"+1]:hover {
        background-color: #d48806;
      }
      .spacer {
        height: 1rem;
      }
    </style>
    """, unsafe_allow_html=True)
    # — 제목
    st.markdown('<div class="option-title">📷 ESL 사진을 업로드하거나<br>카메라로 직접 촬영해 주세요!</div>', unsafe_allow_html=True)

    # — 버튼 2단 레이아웃
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button('📸 카메라 촬영', key='to_camera'):
            st.session_state.page = 'camera'
    with col2:
        if st.button('📁 이미지 업로드', key='to_image_upload'):
            st.session_state.page = 'image_upload'


