import streamlit as st
import cv2
import numpy as np
from PIL import Image
import base64

def render():
    st.markdown("""
        <style>
        .esl-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        .example-img {
            border-radius: 0.75rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stButton>button {
            width: 100%;
            padding: 0.75rem;
            font-weight: bold;
            border-radius: 0.5rem;
            background-color: #4a6ee0;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #3a59b8;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("📸 전자라벨(ESL) 촬영 안내사항")
    st.markdown("""
    - 라벨이 **정면**으로 보이도록 촬영해 주세요.  
    - **빛 반사**나 **그림자**가 없도록 해주세요.  
    - **흐릿하거나 잘리지 않도록** 선명하게 촬영해 주세요.  
    - **한 라벨만** 나오도록 촬영해 주세요.  
    - 정보가 **잘 보이지 않으면 다시 촬영**해 주세요.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    img = Image.open('my-app/thumbnails/sample.jpg')
    st.markdown("#### ✅ 올바른 전자라벨 사진 예시")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, caption=None, use_container_width=True, output_format="JPEG", channels="RGB")

    st.markdown("---")
    st.markdown("#### 📷 아래 버튼을 눌러 사진을 촬영해 주세요")
    img_file_buffer = st.camera_input("")

    if img_file_buffer is not None:
        st.image(img_file_buffer, caption='촬영한 이미지', use_container_width=True)

    col_left, col_right = st.columns([2, 1])
    with col_left:
        pass
    with col_right:
        if st.button('이미지 사용'):
            if not img_file_buffer:
                st.warning('사진을 촬영해주세요!')
            else:
                bytes_data = img_file_buffer.getvalue()
                img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                st.session_state.image = img
                st.session_state.page = 'img_to_aanlysis'
