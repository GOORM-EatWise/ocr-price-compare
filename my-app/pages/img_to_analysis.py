import streamlit as st
import traceback
import os
import cv2
import json
import difflib
from ocr.paddle_ocr import run_ocr
from preprocessing.preprocess import preprocess_image, detect_and_draw_rectangles
from utils.ocr_utils import ocr_quality_score
from llm.promt_to_json import get_product_info_from_ocr


def price_score(texts):
    import re
    full = " ".join(texts).lower()
    score = 0

    if any(k in full for k in ['원', '₩', '할인', 'sale', '%', '기획']):
        score += 2

    digit_ratio = sum(1 for t in texts if any(c.isdigit() for c in t)) / max(len(texts), 1)
    if digit_ratio > 0.3:
        score += 1

    price_pattern = re.compile(r'[\d,]+원|[\d,]{3,5}')
    if price_pattern.search(full):
        score += 2

    if any(u in full for u in ['g', 'ml', '개당', 'kg', '당']):
        score += 1

    if digit_ratio > 0.2 and any(u in full for u in ['g', '원']):
        score += 1

    nutrition_keywords = ['콜레스테롤', '나트륨', '단백질', '탄수화물', '포화지방', '지방', '당류', '열량', '칼로리']
    lowered_texts = [t.lower() for t in texts]

    for t in lowered_texts:
        for nk in nutrition_keywords:
            if difflib.SequenceMatcher(None, t, nk).ratio() > 0.8:
                score -= 3
                break

    return score


def render():
    # CSS 추가
    st.markdown("""
    <style>
        .confirm-buttons {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
        }
        .confirm-buttons button {
            font-size: 20px !important;
            font-weight: 600 !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            width: 180px;
        }
        .stButton>button:focus {
            outline: none;
            box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.6);
        }
        .info-line {
            font-size: 20px !important;
            font-weight: 600 !important;
            color: #213d85 !important;
            margin-bottom: 16px;
        }
    </style>
    """, unsafe_allow_html=True)


    if 'img_to_analysis_done' not in st.session_state:
        st.session_state.img_to_analysis_done = False

    if 'result_text' not in st.session_state:
        st.session_state.result_text = []

    font_path = 'C:/Windows/Fonts/malgun.ttf'

    if not st.session_state.img_to_analysis_done:
            # 이미지 분석 로직
            try:
                img = st.session_state.image

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
                        json.dump(ori_text, f, ensure_ascii=False, indent=2)

                proc_img = preprocess_image(best_crop)
                proc_text, _ = run_ocr(
                    proc_img, font_path,
                    save_json='my-app/json_proc/ocr_result.json',
                    save_annotated='my-app/annotated_proc/annotated.jpg'
                )

                st.session_state.result_text = proc_text

            except Exception:
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

    st.header("📦 추출된 상품 상세정보")

    st.markdown('<h4>✅ 분석 결과</h4>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-line">• <b>제품명:</b> {product_info.get("product_name", "—")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-line">• <b>회사 명:</b> {product_info.get("company_name", "—")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-line">• <b>검색 키워드:</b> {product_info.get("search_keyword", "—")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧐 분석하려는 상품이 맞습니까?")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ 예"):
            st.session_state.page = 'crawling'
    with col2:
        if st.button("🔄 아니오"):
            st.session_state.clear()
            st.session_state.page = 'image_upload_option'