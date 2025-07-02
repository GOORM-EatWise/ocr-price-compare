import streamlit as st
import cv2
import numpy as np


def render():
    img_file_buffer = st.camera_input("Take a picture")

    # 촬영 즉시 이미지 미리보기
    if img_file_buffer is not None:
        st.image(img_file_buffer, caption="촬영한 이미지", uuse_container_width=True)

    if st.button("이미지 사용"):
        if not img_file_buffer:
            st.warning("사진을 촬영해주세요!")
        else:
            bytes_data = img_file_buffer.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            st.session_state.image = img
            st.session_state.page = "img_to_analysis"
