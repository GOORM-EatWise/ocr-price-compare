import streamlit as st
import base64
import os
import sys
from ocr.paddle_ocr import run_ocr
from llm.promt_to_json import get_product_info_from_ocr
from utils.ocr_utils import ocr_quality_score
from preprocessing.preprocess import preprocess_image
import os
import cv2 
import traceback
import pandas as pd


def render():
    if 'img_to_analysis_done' not in st.session_state:
        st.session_state.img_to_analysis_done = False
        
    if 'result_text' not in st.session_state:
        st.session_state.result_text = []

    font_path = 'C:/Windows/Fonts/malgun.ttf' 
    
    if not st.session_state.img_to_analysis_done:
        #st.title("로딩 중....")
        
        with st.spinner("text 추출 중입니다..."):
        # image -> text -> AI(Gemini)
            try:
                print("이미지 텍스트 변환 시도")
                
                ori_text, _ = run_ocr(st.session_state.image, font_path, save_json = 'c:\\Users\\jiwoong\\Desktop\\VS Code\\EatWise\\Streamlit_UI\\json\\ocr_result.json', save_annotated = 'c:\\Users\\jiwoong\\Desktop\\VS Code\\EatWise\\Streamlit_UI\\annotated\\annotated.jpg')
                proc_img = preprocess_image(st.session_state.image)
                proc_text, _ = run_ocr(proc_img, font_path, save_json = 'c:\\Users\\jiwoong\\Desktop\\VS Code\\EatWise\\Streamlit_UI\\json_proc\\ocr_result.json', save_annotated = 'c:\\Users\\jiwoong\\Desktop\\VS Code\\EatWise\\Streamlit_UI\\annotated_proc\\annotated.jpg')
                
                score_o = ocr_quality_score(ori_text)
                score_p = ocr_quality_score(proc_text)
                
                result_text = proc_text if score_p > score_o else ori_text
                                
                st.session_state.result_text = result_text
                
            except Exception as e:
                print(f"이미지 텍스트 변환 실패")
                traceback.print_exc()
                st.session_state.page = 'image_upload_option'
            else:
                print("이미지 텍스트 변환 성공")
                st.session_state.img_to_analysis_done = True
                st.rerun()
    
    ocr_texts = [item["text"] for item in st.session_state.result_text]
    
    product_info = get_product_info_from_ocr(ocr_texts, save_path='c:\\Users\\jiwoong\\Desktop\\VS Code\\EatWise\\Streamlit_UI\\llm_json\\llm_result.json')

    st.session_state.ocr_texts = ocr_texts

    st.session_state.product_info = product_info
    
    st.header("추출된 상품 상세정보")

    st.write("**제품명:**", product_info["product_name"])
    st.write("**회사 명:**", product_info["company_name"])
    st.write("**검색 키워드:**", product_info["search_keyword"])
    
    st.markdown("---")
    st.write("### 분석하려는 상품이 맞습니까?")
    
    col_yes, col_no = st.columns(2)
    
    with col_yes:
        if st.button('예'):
            st.session_state.page = 'crawling'
    with col_no:
        if st.button('아니오'):
            st.session_state.page = 'image_upload_option'
    
    
    # if st.button('다음으로'):
    #     st.session_state.page = 'crawling'