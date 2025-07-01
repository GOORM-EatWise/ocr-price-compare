import streamlit as st

def render():
    # st.title('정보를 입력해주세요')
    
    st.markdown("""
    ## 🍎 EatWise에 오신 것을 환영합니다!
    
    **EatWise**는 상품 가격표를 촬영하면 자동으로 영양성분과 가격을 
    비슷한 제품들과 비교 분석해주는 스마트 쇼핑 도우미입니다.
    
    ### ✨ 주요 기능
    - 📸 **이미지 인식**: 상품 가격표 촬영으로 OCR을 통한 상품 Text 추출
    - 🤖 **AI 텍스트 분류**: LLM을 활용하여 추출된 텍스트에서 상품명, 영양성분 등을 자동 분류
    - 🔍 **영양성분 분석**: 개인 맞춤형 영양 정보 제공
    - 💰 **가격 비교**: 다양한 쇼핑몰의 최저가 검색
    
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