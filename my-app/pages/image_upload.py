import streamlit as st
import numpy as np
from PIL import Image
import time

def render():
    # CSS 정의
    st.markdown("""
    <style>
      .reportview-container .main .block-container {
          background-color: #f9f9fb !important;
          padding: 2rem !important;
          border-radius: 1rem !important;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
          max-width: 800px;
          margin: 2rem auto;
      }
      .reportview-container .main .block-container h1 {
          text-align: center;
          color: #3b63c4;
      }
      .reportview-container .main .block-container img {
          border-radius: 0.5rem;
      }
      .stButton>button {
          display: block;
          width: 50%;
          min-width: 200px;
          margin: 1rem auto 0;
          padding: 0.8rem 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: white;
          background: linear-gradient(135deg, #6C63FF 0%, #3b63c4 100%);
          border: none;
          border-radius: 0.75rem;
          transition: background 0.3s ease, transform 0.1s ease;
      }
      .stButton>button:hover {
          background: linear-gradient(135deg, #5a54e5 0%, #2d4fa1 100%);
          transform: translateY(-2px);
      }
    </style>
    """, unsafe_allow_html=True)

    # 제목
    st.header("전자라벨(ESL) 이미지 업로드 안내사항")

    # 강조된 안내사항
    st.markdown("""
    <ul style="font-size: 1.05rem; line-height: 1.6;">
      <li><span style="color:#2d3a7c; font-weight:600;">촬영 당시 라벨이 선명하게</span> 보이는 이미지를 선택해 주세요.</li>
      <li>이미지에 <span style="color:#2d3a7c; font-weight:600;">빛 반사나 그림자</span>가 없어야 <span style="font-weight:600;">정확한 인식</span>이 가능합니다.</li>
      <li>라벨 전체가 <span style="color:#2d3a7c; font-weight:600;">잘려있지 않고 완전히 포함된 이미지</span>를 업로드해 주세요.</li>
      <li><span style="color:#2d3a7c; font-weight:600;">한 상품 라벨만</span> 포함된 사진이 더 좋은 결과를 제공합니다.</li>
      <li><span style="color:#d9534f; font-weight:600;">흐릿하거나 흔들린 이미지</span>는 인식률이 떨어질 수 있으니 주의해 주세요.</li>
    </ul>
    """, unsafe_allow_html=True)

    # 예시 이미지
    sample = Image.open('my-app/thumbnails/sample.jpg').resize((600, 600))
    st.image(sample, caption='올바른 전자라벨(ESL) 사진 예시', use_container_width=True)

    # 이미지 업로드
    uploaded_file = st.file_uploader("이미지 선택 (.png, .jpg, .jpeg)", type=['png', 'jpg', 'jpeg'])

    rotated = None
    if uploaded_file:
        if 'rotation' not in st.session_state:
            st.session_state.rotation = 0

        img_upload = Image.open(uploaded_file)
        rotated = img_upload.rotate(-st.session_state.rotation, expand=True)

        # 회전값이 없어도 항상 이미지 미리보기 아래에 위치
        st.image(rotated, caption=f'업로드한 이미지 (회전: {st.session_state.rotation}°)', use_container_width=True)


    # 하단 버튼 영역
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⟳ 90° 회전"):
            st.session_state.rotation = (st.session_state.rotation + 90) % 360
            st.rerun()

    with col2:
        if st.button("이미지 사용"):
            st.session_state.image = np.asarray(rotated)
            st.session_state.page = 'img_to_analysis'

if __name__ == "__main__":
    render()
