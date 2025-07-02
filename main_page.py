import streamlit as st
from pages import get_user_info
from pages import eatwise_info
from pages import image_upload_option
from pages import image_upload
from pages import camera
from pages import img_to_analysis
from pages import crawling
from pages import result

# 페이지 이름과 표시할 카테고리 이름 매핑
page_names = [
    'get_user_info',
    'eatwise_info',
    'image_upload_option', 
    'image_upload',
    'camera',
    'img_to_analysis',
    'crawling',
    'result'
]

page_labels = [
    '👤 사용자 정보 입력',
    '🍏 EatWise 설명',
    '📂 이미지 업로드 옵션',
    '📷 이미지 업로드',
    '📸 카메라 촬영',
    '🔍 이미지 분석',
    '🌐 크롤링',
    '📊 결과 보기'
]

# 사이드바에 카테고리 메뉴 생성
st.sidebar.title('🍎 EatWise 메뉴')
st.sidebar.markdown("---")

#현재 페이지에 해당하는 라벨 찾기
current_page_index = 0
if 'page' in st.session_state:
    try:
        current_page_index = page_names.index(st.session_state.page)
    except ValueError:
        current_page_index = 0

# 라디오 버튼으로 페이지 선택
selected_page_label = st.sidebar.radio(
    '페이지 선택', 
    page_labels,
    index=current_page_index
)

# 선택된 라벨에 맞는 페이지 이름 찾기
selected_page_index = page_labels.index(selected_page_label)
selected_page_name = page_names[selected_page_index]

# 세션 상태 업데이트
st.session_state.page = selected_page_name

# 페이지 이동 처리 (기존 코드 유지)
if st.session_state.page == 'get_user_info':
    get_user_info.render() 
elif st.session_state.page == 'eatwise_info':
    eatwise_info.render()     
elif st.session_state.page == 'image_upload_option':
    image_upload_option.render()
elif st.session_state.page == 'image_upload':
    image_upload.render()
elif st.session_state.page == 'camera':
    camera.render()
elif st.session_state.page == 'img_to_analysis':
    img_to_analysis.render()
elif st.session_state.page == 'crawling':
    crawling.render()
elif st.session_state.page == 'result':
    result.render()