import streamlit as st

def render():
    st.markdown("""
    <div style="text-align: center;">
        <h2> EatWise란?</h2>
        <p>
            <b>EatWise</b>는 전자 가격 표시기(ESL)를 촬영하면<br>
            <b>OCR</b>과 <b>AI</b> 기술을 활용해<br>
            <b>상품명, 영양성분, 가격</b> 정보를 자동으로 추출하고,<br>
            다양한 제품과의 <b>영양 및 가격 비교</b>를 손쉽게 도와주는<br>
            <b>스마트 쇼핑 도우미</b>입니다.
        </p>
        <p>
            <h4>주요 특징</h4>
            - 이미지 업로드 또는 카메라 촬영으로 간편하게 AI OCR를 통한 <b>상품 정보 인식<b><br>
            - <b>AI OCR 기반 텍스트 분류<b>로 정확한 상품명과 영양성분 자동 추출<br>
            - 맞춤형 영양 정보와 가격 비교 분석 제공<br>
            - 직관적인 데이터 시각화와 사용자 친화적 UI
        </p>
        <p>
            EatWise와 함께라면<br>
            건강한 식품 선택과 합리적인 쇼핑이 더 쉬워집니다!
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button('처음 페이지로 돌아가기', key='back_to_main'):
        st.session_state.page = 'get_user_info'

