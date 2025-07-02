import streamlit as st
from PIL import Image

def render():
    
    img = Image.open('thumbnails/EatWise_logo.png')
    img = img.resize((200, 200))
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(img)
    
    st.markdown("""
                ## EatWise에 오신 것을 환영합니다!
    """)   
    
    st.markdown("👇EatWise가 궁금하시면")
    
    if st.button('EatWise란?', key='to_eatwise_info'):
        st.session_state.page = 'eatwise_info'
    
    st.markdown("""
    아래 정보를 입력하시면 더 정확한 맞춤 분석을 받으실 수 있습니다.
    """)    

    user_name = st.text_input('이름', value="User")
    gender = st.selectbox('성별', ['남', '여'])
    height = st.number_input('키(cm 단위로 숫자만 입력해주세요)', min_value=0, value=165)
    weight = st.number_input('몸무게(kg 단위로 숫자만 입력해주세요)', min_value=0, value=65)
    age = st.number_input('나이(숫자로 입력해주세요)', min_value=0, value=25)

    if 'user_info' not in st.session_state:
        st.session_state.user_info = dict()

    st.session_state.user_info['user_name'] = user_name
    st.session_state.user_info['gender'] = gender
    st.session_state.user_info['height'] = height
    st.session_state.user_info['weight'] = weight
    
    if st.button('다음', key='to_image_upload_option'):
        st.session_state.page = 'image_upload_option'