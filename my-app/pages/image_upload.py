import streamlit as st
import numpy as np
from PIL import Image

def render():
    st.header("전자라벨(ESL) 이미지 업로드 안내사항")
    
    st.markdown("""
    - 촬영 당시 라벨이 선명하게 보이는 이미지를 선택해 주세요.
    - 이미지에 빛 반사나 그림자가 없어야 정확한 인식이 가능합니다.
    - 라벨 전체가 잘려있지 않고 전체가 포함된 이미지를 업로드해 주세요.
    - 여러 상품이 함께 찍힌 사진보다는 한 번에 한 상품 라벨이 포함된 사진이 좋습니다.
    - 흐릿하거나 흔들린 이미지는 인식률이 떨어질 수 있으니 주의해 주세요.
    """)
    
    img = Image.open('my-app/thumbnails/sample.jpg')
    img = img.resize((1000, 1000))
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(img, caption='올바른 전자라벨(ESL) 사진 예시')

    uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg'])
    
    # 업로드 즉시 이미지 미리보기
    if uploaded_file is not None:
        st.image(uploaded_file, caption='업로드한 이미지', use_container_width=True)
    
    #버튼 가운데 정렬
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:    
        if st.button('이미지 사용'):
            if not uploaded_file:
                st.warning('이미지를 업로드 해주세요!')
            else:
                st.session_state.image = np.asarray(Image.open(uploaded_file))
                st.session_state.page = 'img_to_analysis'