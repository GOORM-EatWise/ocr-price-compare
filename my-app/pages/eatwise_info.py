import streamlit as st

def render():
    st.markdown("""
    <style>
      .intro-card {
        max-width: 720px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: #f9f9fb;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
      }
      .intro-title {
        color: #3b63c4;
        font-size: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
      }
      .intro-subtitle {
        color: #2d3a7c;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
      }
      .intro-text {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #333;
        margin-bottom: 1rem;
      }
      .highlight {
        color: #2d3a7c;
        font-weight: bold;
      }
      .brand-highlight {
        color: #d9534f;
        font-weight: bold;
      }
      .feature-list {
        text-align: center;     
        margin: 1rem 0;
        padding: 0;             
      }
      .feature-item {
        display: inline-block;  
        font-size: 1.05rem;
        line-height: 1.7;
        color: #333;
        margin: 0.5rem 1rem;    
        text-align: left;       
      }
      .stButton>button {
        background-color: #3b63c4;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        margin-top: 1.5rem;
      }
      .stButton>button:hover {
        background-color: #2d4fa1;
      }
    </style>

    <div class="intro-card">
      <div class="intro-title">EatWise란?</div>

      <div class="intro-text">
        <span class="highlight">EatWise</span>는 전자 가격 표시기(ESL)를 촬영하면,<br>
        <span class="highlight">OCR</span>과 <span class="highlight">AI</span> 기술을 활용해<br>
        <span class="highlight">상품명, 영양성분, 가격</span> 정보를 자동 추출하고,<br>
        다양한 제품과의 <span class="highlight">영양 및 가격 비교</span>를 도와주는<br>
        <span class="brand-highlight">스마트 쇼핑 도우미</span>입니다.
      </div>

      <div class="intro-subtitle">주요 특징</div>
      <div class="feature-list">
        <div class="feature-item">✔️ 카메라 촬영 또는 이미지 업로드로 간편한 OCR 사용</div>
        <div class="feature-item">✔️ <span class="highlight">AI 기반 텍스트 분류</span>로 상품명과 영양성분 자동 추출</div>
        <div class="feature-item">✔️ 맞춤형 <span class="highlight">영양 정보 & 가격 비교 분석</span> 제공</div>
        <div class="feature-item">✔️ 직관적인 데이터 시각화와 사용자 친화적인 UI</div>
      </div>

      <div class="intro-text" style="margin-top:2rem;">
        EatWise와 함께라면<br>
        <span class="highlight">건강한 식품 선택</span>과 <span class="highlight">합리적인 쇼핑</span>이 더 쉬워집니다!
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button('처음 페이지로 돌아가기', key='back_to_main'):
        st.session_state.page = 'get_user_info'

# 페이지가 이 모듈을 직접 실행했을 때만 render() 호출
if __name__ == "__main__":
    render()
