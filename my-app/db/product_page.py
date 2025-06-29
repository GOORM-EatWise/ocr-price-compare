import streamlit as st
import pandas as pd
import os
import sys
import subprocess
import json
import time
from google import genai
from google.genai import types


# 현재 파일의 절대 경로를 기준으로 상위 디렉토리 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


def run_crawler(crawler_name, search_keyword, pages=4):
    """별도의 Python 프로세스에서 크롤러를 실행하는 함수"""
    try:
        # 크롤링 디렉토리로 이동
        crawling_dir = os.path.join(parent_dir, "crawling")

        # scrapy 명령어 실행
        command = f"cd {crawling_dir} && scrapy crawl {crawler_name} -a search_keyword='{search_keyword}' -a pages={pages}"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=180,  # 3분 타임아웃
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "데이터 로드가 완료되었습니다!",
                "output": result.stdout,
            }
        else:
            return {"status": "error", "message": f"크롤링 중 오류: {result.stderr}"}

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "크롤링 시간이 초과되었습니다."}
    except Exception as e:
        return {"status": "error", "message": f"오류 발생: {str(e)}"}


def check_crawling_result(search_keyword):
    """크롤링 결과 파일이 생성되었는지 확인"""
    crawling_dir = os.path.join(parent_dir, "crawling")
    result_file = os.path.join(crawling_dir, f"{search_keyword}_nutrition_data.json")

    if os.path.exists(result_file):
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"status": "success", "data": data, "count": len(data)}
        except Exception as e:
            return {"status": "error", "message": f"결과 파일 읽기 오류: {str(e)}"}
    else:
        return {"status": "error", "message": "크롤링 결과 파일을 찾을 수 없습니다."}


def search_product_data(product_name):
    """데이터 검색"""

    # 메시지 컨테이너 생성
    message_container = st.empty()

    prod_result = run_crawler("product", product_name)

    if prod_result["status"] == "success":
        message_container.success(prod_result["message"])

        # 결과 확인
        time.sleep(0.5)  # 파일 생성 대기
        check_result = check_crawling_result(product_name)

        if check_result["status"] == "success" and int(check_result["count"]) > 0:
            message_container.success("데이터를 찾았습니다.")
            data_list = []
            for item in check_result["data"]:
                data_dict = {
                    "spec_origin": item["spec_origin"],  # type: ignore
                    "prod_name": item["prod_name"],  # type: ignore
                    "price": item["price"],  # type: ignore
                    "per_serving": item["per_serving"],  # type: ignore
                    "kcal": item["kcal"],  # type: ignore
                    "carb": item["carb"],  # type: ignore
                    "sugar": item["sugar"],  # type: ignore
                    "protein": item["protein"],  # type: ignore
                    "fat": item["fat"],  # type: ignore
                }
                data_list.append(data_dict)

            return data_list
        else:
            message_container.error(check_result["message"])
            return None
    else:
        message_container.error(prod_result.get("message", "크롤링에 실패했습니다."))
        return None


def generate_search_keyword(product_name):
    """검색 키워드 생성"""

    GEMINI_API_KEY = "AIzaSyCx4nVj9b89vZPPGJRe_G7F-elJwArQiMk"

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""Generate a core keyword for similar products to {product_name}, generate only one keyword in Korean. """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=1024),
    )

    return response.text


def search_similar_product(product_name):
    """유사 상품 검색"""

    search_keyword = generate_search_keyword(product_name)

    # 메시지 컨테이너 생성
    message_container = st.empty()

    prod_result = run_crawler("product", search_keyword)

    if prod_result["status"] == "success":
        message_container.success(prod_result["message"])

        # 결과 확인
        time.sleep(0.5)  # 파일 생성 대기
        check_result = check_crawling_result(search_keyword)

        if check_result["status"] == "success" and int(check_result["count"]) > 0:
            message_container.success("데이터를 찾았습니다.")
            data_list = []
            for item in check_result["data"]:
                data_dict = {
                    "spec_origin": item["spec_origin"],  # type: ignore
                    "prod_name": item["prod_name"],  # type: ignore
                    "price": item["price"],  # type: ignore
                    "per_serving": item["per_serving"],  # type: ignore
                    "kcal": item["kcal"],  # type: ignore
                    "carb": item["carb"],  # type: ignore
                    "sugar": item["sugar"],  # type: ignore
                    "protein": item["protein"],  # type: ignore
                    "fat": item["fat"],  # type: ignore
                }
                data_list.append(data_dict)

            return data_list
        else:
            message_container.error(check_result["message"])
            return None
    else:
        message_container.error(prod_result.get("message", "크롤링에 실패했습니다."))
        return None


st.set_page_config(
    page_title="Product Info",
    page_icon="🍔",
)

st.title("상품 정보 크롤링")

with st.form(key="product_add_form", clear_on_submit=False):
    product_name = st.text_input("상품 이름")

    submit = st.form_submit_button("크롤링 시작")

    if submit and product_name:
        # 데이터 표시 컨테이너 생성
        data_container_top = st.empty()
        data_container_bottom = st.empty()

        with st.spinner("데이터를 찾는 중입니다..."):
            # 크롤링 실행
            data_list = search_product_data(product_name)

            if data_list:
                data_df = pd.DataFrame(data_list)
                data_container_top.dataframe(data_df.iloc[:, 1:])
            else:
                data_container_top.info("데이터를 찾을 수 없습니다.")

        with st.spinner("유사 상품을 찾는 중입니다..."):
            if data_list:
                similar_data_list = search_similar_product(product_name)
                if similar_data_list:
                    similar_data_df = pd.DataFrame(similar_data_list)
                    data_container_bottom.dataframe(similar_data_df.iloc[:, 1:])
                else:
                    data_container_bottom.info("유사 상품을 찾을 수 없습니다.")

    save_data = st.form_submit_button("데이터 저장")

    if save_data:
        pass
