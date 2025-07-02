import streamlit as st
import traceback
import os
import cv2
import pandas as pd
from ocr.paddle_ocr import run_ocr
from preprocessing.preprocess import preprocess_image, detect_and_draw_rectangles
from utils.ocr_utils import ocr_quality_score
from llm.promt_to_json import get_product_info_from_ocr
import difflib

def price_score(texts):
    import re
    full = " ".join(texts).lower()
    score = 0

    # 핵심 키워드
    if any(k in full for k in ['원', '₩', '할인', 'sale', '%', '기획']):
        score += 2

    # 숫자 포함 비율
    digit_ratio = sum(1 for t in texts if any(c.isdigit() for c in t)) / max(len(texts), 1)
    if digit_ratio > 0.3:
        score += 1

    # 가격형 패턴
    price_pattern = re.compile(r'[\d,]+원|[\d,]{3,5}')
    if price_pattern.search(full):
        score += 2

    #  단위 키워드
    if any(u in full for u in ['g', 'ml', '개당', 'kg', '당']):
        score += 1

    # 숫자 + 단위 조합
    if digit_ratio > 0.2 and any(u in full for u in ['g', '원']):
        score += 1

    # 감점: 유사한 영양성분 키워드 포함 시
    nutrition_keywords = ['콜레스테롤', '나트륨', '단백질', '탄수화물', '포화지방', '지방', '당류', '열량', '칼로리']
    lowered_texts = [t.lower() for t in texts]

    for t in lowered_texts:
        for nk in nutrition_keywords:
            # 유사도가 0.8 이상이면 감점
            if difflib.SequenceMatcher(None, t, nk).ratio() > 0.8:
                score -= 3
                break

    return score


def render():
    if 'img_to_analysis_done' not in st.session_state:
        st.session_state.img_to_analysis_done = False
        
    if 'result_text' not in st.session_state:
        st.session_state.result_text = []

    font_path = 'C:/Windows/Fonts/malgun.ttf' 
    
    if not st.session_state.img_to_analysis_done:
        st.title("로딩 중....")
        
        with st.spinner("이미지를 분석 중입니다..."):
            try:
                img = st.session_state.image

                # 1. 사각형(ROI) 추출
                rects, crops = detect_and_draw_rectangles(img)

                best_crop = None
                best_score = -1
                best_ocr_data = []

                for (x, y, w, h), crop_img in zip(rects, crops):
                    ocr_data, _ = run_ocr(crop_img, font_path)
                    texts = [d["text"] for d in ocr_data]
                    score = price_score(texts)

                    if score > best_score:
                        best_score = score
                        best_crop = crop_img
                        best_ocr_data = ocr_data

                # 2. ROI가 없거나 점수 ≤ 1이면 → 원본 사용
                if not crops or best_score <= 1:
                    best_crop = img
                    ori_text, _ = run_ocr(
                        best_crop, font_path,
                        save_json='my-app/json/ocr_result.json',
                        save_annotated='my-app/annotated/annotated.jpg'
                    )
                else:
                    ori_text = best_ocr_data
                    os.makedirs('my-app/json', exist_ok=True)
                    with open('my-app/json/ocr_result.json', 'w', encoding='utf-8') as f:
                        import json
                        json.dump(ori_text, f, ensure_ascii=False, indent=2)

                # 3. 전처리 후 OCR
                proc_img = preprocess_image(best_crop)
                proc_text, _ = run_ocr(
                    proc_img, font_path,
                    save_json='my-app/json_proc/ocr_result.json',
                    save_annotated='my-app/annotated_proc/annotated.jpg'
                )

                # ✅ 전처리 결과 무조건 사용
                st.session_state.result_text = proc_text

            except Exception as e:
                print("⚠️ 이미지 텍스트 변환 실패")
                traceback.print_exc()
                st.session_state.page = 'image_upload_option'
            else:
                print("✅ 이미지 텍스트 변환 성공")
                st.session_state.img_to_analysis_done = True
                st.rerun()

    ocr_texts = [item["text"] for item in st.session_state.result_text]
    product_info = get_product_info_from_ocr(ocr_texts, save_path='my-app/llm_json/llm_result.json')

    st.session_state.ocr_texts = ocr_texts
    st.session_state.product_info = product_info

    st.header("추출된 상품 상세정보")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**제품명:**")
        st.write("**회사 명:**")
        st.write("**검색 키워드:**")
    with col2:
        st.write(product_info.get("product_name", "—"))
        st.write(product_info.get("company_name", "—"))
        st.write(product_info.get("search_keyword", "—"))

    if st.button('다음으로'):
        st.session_state.page = 'crawling'
