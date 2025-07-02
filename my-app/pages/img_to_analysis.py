import streamlit as st
import base64
from ocr.paddle_ocr import run_ocr
from llm.promt_to_json import get_product_info_from_ocr
from utils.ocr_utils import ocr_quality_score
from preprocessing.preprocess import preprocess_image
import os
import cv2

# import get_product_info_from_ocr
# import run_ocr
import traceback
import pandas as pd


current_path = os.path.dirname(os.path.abspath(__file__))


def render():
    if "img_to_analysis_done" not in st.session_state:
        st.session_state.img_to_analysis_done = False

    if "result_text" not in st.session_state:
        st.session_state.result_text = []

    font_path = os.path.join(current_path, "../font/NanumGothic.ttf")

    if not st.session_state.img_to_analysis_done:
        st.title("로딩 중....")

        with st.spinner("이미지를 분석 중입니다..."):
            # image -> text -> AI(Gemini)
            try:
                print("이미지 텍스트 변환 시도")

                ori_text, _ = run_ocr(
                    st.session_state.image,
                    font_path,
                    save_json=os.path.join(current_path, "../json/ocr_result.json"),
                    save_annotated=os.path.join(
                        current_path, "../annotated/annotated.jpg"
                    ),
                )
                proc_img = preprocess_image(st.session_state.image)
                proc_text, _ = run_ocr(
                    proc_img,
                    font_path,
                    save_json=os.path.join(
                        current_path, "../json_proc/ocr_result.json"
                    ),
                    save_annotated=os.path.join(
                        current_path, "../annotated_proc/annotated.jpg"
                    ),
                )

                score_o = ocr_quality_score(ori_text)
                score_p = ocr_quality_score(proc_text)

                result_text = proc_text if score_p > score_o else ori_text

                st.session_state.result_text = result_text

            except Exception as e:
                print(f"이미지 텍스트 변환 실패")
                traceback.print_exc()
                st.session_state.page = "image_upload_option"
            else:
                print("이미지 텍스트 변환 성공")
                st.session_state.img_to_analysis_done = True
                st.rerun()

    ocr_texts = [item["text"] for item in st.session_state.result_text]

    product_info = get_product_info_from_ocr(
        ocr_texts,
        save_path="../llm_json/llm_result.json",
    )

    st.session_state.ocr_texts = ocr_texts

    st.session_state.product_info = product_info

    st.header("추출된 상품 상세정보")
    # st.json(product_info)  # 또는 st.write(product_info)

    # DataFrame으로 변환
    # display_data = {
    #     "항목": ["제품명", "제품 종류", "검색을 위한 키워드"],
    #     "내용": [product_info["product_name"], product_info["product_type"], product_info["search_keyword"]]}

    # df = pd.DataFrame(display_data)

    # st.table(df)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("**제품명:**")
        st.write("**회사 명:**")
        st.write("**검색 키워드:**")

    with col2:
        st.write(product_info["product_name"])
        st.write(product_info["company_name"])
        st.write(product_info["search_keyword"])

    if st.button("다음으로"):
        st.session_state.page = "crawling"
