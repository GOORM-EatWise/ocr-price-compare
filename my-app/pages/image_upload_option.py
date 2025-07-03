import streamlit as st

def render():
    
    # st.header('이미지 업로드 방식 선택')
    
    # 안내 멘트와 이모지
    st.markdown("""
    <div style='text-align:center; font-size:22px;'>
        📷 <b>전자라벨(ESL) 사진을 업로드하거나<br>카메라로 직접 촬영해 주세요!</b>
    </div>
    """, unsafe_allow_html=True)
    
    #공백
    st.write("")
    st.write("")
    
    if 'image' not in st.session_state:
        st.session_state.image = None
    
    if st.button('카메라 촬영', key='to_camera'):
        st.session_state.page = 'camera'
    
    if st.button('이미지 업로드', key='to_image_upload'):
        st.session_state.page = 'image_upload'    
    
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button('카메라 직접 촬영', key='to_camera'):
    #         st.session_state.page = 'camera'
    # with col2:
    #     if st.button('이미지 업로드', key='to_image_upload'):
    #         st.session_state.page = 'image_upload'