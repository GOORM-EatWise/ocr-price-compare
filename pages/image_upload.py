import streamlit as st
import numpy as np
from PIL import Image

def render():
    st.title('이미지를 업로드 해주세요')

    uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg'])
    
    # 업로드 즉시 이미지 미리보기
    if uploaded_file is not None:
        st.image(uploaded_file, caption='업로드한 이미지', use_container_width=True)
        
    if st.button('이미지 사용'):
        if not uploaded_file:
            st.warning('이미지를 업로드 해주세요!')
        else:
            st.session_state.image = np.asarray(Image.open(uploaded_file))
            st.session_state.page = 'img_to_analysis'