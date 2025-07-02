import streamlit as st
import cv2
import numpy as np
from PIL import Image

def render():
    st.header("전자라벨(ESL) 촬영 안내사항")
    
    st.markdown("""
    - 라벨이 화면에 정면으로 오도록 촬영해 주세요.
    - 빛 반사나 그림자가 없도록 해주세요.
    - 라벨 전체가 잘리거나 흐릿하지 않게 선명하게 찍어주세요.
    - 여러 상품이 함께 나오지 않도록, 한 번에 한 라벨만 촬영해 주세요.
    - 촬영 후 이미지를 확인하고, 정보가 잘 보이지 않으면 다시 촬영해 주세요.
    """)
    
    img = Image.open('thumbnails/sample.jpg')
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(img, caption='올바른 전자라벨(ESL) 사진 예시', use_container_width=True)
    
    img_file_buffer = st.camera_input("Take a picture")
    
    # 촬영 즉시 이미지 미리보기
    if img_file_buffer is not None:
        st.image(img_file_buffer, caption='촬영한 이미지', uuse_container_width=True)
        
    if st.button('이미지 사용'):
        if not img_file_buffer:
            st.warning('사진을 촬영해주세요!')
        else:
            bytes_data = img_file_buffer.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            st.session_state.image = img
            st.session_state.page = 'img_to_aanlysis'