import streamlit as st

def render():
    if 'image' not in st.session_state:
        st.session_state.image = None
    
    if st.button('카메라 촬영', key='to_camera'):
        st.session_state.page = 'camera'

    if st.button('이미지 업로드', key='to_image_upload'):
        st.session_state.page = 'image_upload'