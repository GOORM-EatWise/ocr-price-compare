import streamlit as st
from PIL import Image
import io
import base64

def render():
    # — CSS 정의
    st.markdown("""
    <style>
      .welcome-card {
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        text-align: center;
      }
      /* st.image로 렌더된 img 태그에 적용 */
      .welcome-card img {
        width: 120px !important;
        height: auto !important;
        margin-bottom: 1rem;
      }
      .welcome-title {
        font-size: 2rem;
        color: #3b63c4;
        font-weight: bold;
        margin-bottom: 0.5rem;
      }
      .welcome-subtitle {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
      }
      .stTextInput>div>div>input,
      .stNumberInput>div>div>input,
      .stSelectbox>div>div>div>div {
        border-radius: 0.5rem;
      }
      .stButton>button {
        background-color: #3b63c4;
        color: white;
        font-weight: bold;
        padding: 0.6rem 1.2rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        width: 100%;
      }
      .stButton>button:hover {
        background-color: #2d4fa1;
      }
    </style>
    """, unsafe_allow_html=True)

    # — Logo 중앙 배치
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        img = Image.open('my-app/thumbnails/EatWise_logo.png')
        st.image(img)  # width는 CSS로 제어

    # — 타이틀 & 부제
    st.markdown('<div class="welcome-title">EatWise에 오신 것을 환영합니다!</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-subtitle">간단한 정보만 입력하시면 맞춤형 분석이 제공됩니다.</div>', unsafe_allow_html=True)

    # — EatWise Info 버튼
    if st.button('🤔 EatWise란?', key='to_eatwise_info'):
        st.session_state.page = 'eatwise_info'

    st.markdown("---")

    # — 2단 입력 폼
    user_name = st.text_input('이름', value="User")
    gender = st.selectbox('성별', ['남', '여'])
    height_col, weight_col = st.columns(2)
    with height_col:
        h = st.number_input('키 (cm)', min_value=0, value=165)
    with weight_col:
        w = st.number_input('몸무게 (kg)', min_value=0, value=65)
    age = st.number_input('나이', min_value=0, value=25)

    # — 세션에 저장
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    st.session_state.user_info.update({
        'user_name': user_name,
        'gender': gender,
        'height': h,
        'weight': w,
        'age': age
    })

    # — 다음 버튼
    if st.button('다음', key='to_image_upload_option'):
        st.session_state.page = 'image_upload_option'


if __name__ == "__main__":
    render()
