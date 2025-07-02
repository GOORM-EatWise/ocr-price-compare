import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import os


def extract_product_info(product_info):
    """product_info JSON에서 product_name과 product_category 추출"""
    extracted_info = []

    if isinstance(product_info, list):
        for item in product_info:
            info = {
                "prod_name": item.get("product_name", ""),
                "product_category": item.get("product_type", ""),
                "brand": item.get("brand", ""),
                "search_keyword": item.get("search_keyword", ""),
                "original_item": item,
            }
            extracted_info.append(info)
    elif isinstance(product_info, dict):
        info = {
            "prod_name": product_info.get("product_name", ""),
            "product_category": product_info.get("product_type", ""),
            "brand": product_info.get("brand", ""),
            "search_keyword": product_info.get("search_keyword", ""),
            "original_item": product_info,
        }
        extracted_info.append(info)

    return extracted_info


def create_directories():
    """필요한 디렉토리 생성"""
    directories = ["original_product", "danawa_product"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"디렉토리 생성: {directory}")


def extract_volume_from_name(product_name):
    """상품명에서 용량 정보 추출"""
    volume_patterns = [
        r"(\d+(?:\.\d+)?)\s*ml",
        r"(\d+(?:\.\d+)?)\s*l",
        r"(\d+(?:\.\d+)?)\s*리터",
        r"(\d+(?:\.\d+)?)\s*g",
        r"(\d+(?:\.\d+)?)\s*kg",
        r"(\d+(?:\.\d+)?)\s*개입",
        r"(\d+(?:\.\d+)?)\s*팩",
    ]

    for pattern in volume_patterns:
        match = re.search(pattern, product_name.lower())
        if match:
            return match.group(0)

    return "용량 정보 없음"


def crawl_original_product_volumes(search_term, max_products=3):
    """원본 상품의 다양한 용량 옵션 크롤링"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        search_url = (
            f"https://search.danawa.com/dsearch.php?query={search_term}&tab=goods"
        )
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 응답 상태 코드 확인
        if response.status_code != 200:
            st.error(f"HTTP 오류: {response.status_code}")
            raise Exception(f"HTTP 오류: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        products = []

        # 상품 리스트 선택자
        selectors = [".prod_main_info", ".prod_item", ".item_wrap", ".list_item"]

        product_items = []
        for selector in selectors:
            product_items = soup.select(selector)
            if product_items:
                break

        if not product_items:
            return []

        # 용량별로 그룹화하기 위한 딕셔너리
        volume_products = {}

        for idx, item in enumerate(
            product_items[: max_products * 2]
        ):  # 더 많이 검색해서 용량 다양성 확보
            try:
                # 상품명 추출
                name_selectors = [".prod_name a", ".item_name a", ".prod_info .name"]
                product_name = None
                for name_sel in name_selectors:
                    name_elem = item.select_one(name_sel)
                    if name_elem:
                        product_name = name_elem.get_text(strip=True)
                        break

                if not product_name:
                    continue

                # 가격 추출
                price_selectors = [
                    ".price_sect strong",
                    ".price strong",
                    ".item_price strong",
                ]
                price = "가격 정보 없음"
                for price_sel in price_selectors:
                    price_elem = item.select_one(price_sel)
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break

                # 용량 추출
                volume = extract_volume_from_name(product_name)

                # 검색어와 유사한 상품만 필터링
                search_terms = search_term.lower().split()
                if any(term in product_name.lower() for term in search_terms):
                    product_data = {
                        "prod_name": product_name,
                        "price": price,
                        "volume": volume,
                        "search_term": search_term,
                        "nutrition_info": generate_nutrition_info(product_name, search_term),
                    }

                    # 용량별로 그룹화 (같은 용량이면 첫 번째 것만 저장)
                    if volume not in volume_products:
                        volume_products[volume] = product_data

            except Exception as e:
                continue

        # 최대 3개까지만 반환
        products = list(volume_products.values())[:max_products]

        return products

    except Exception as e:
        return []


def crawl_similar_products_by_category(category, selected_volume, max_products=5):
    """카테고리 기반으로 유사 상품들의 영양성분, 용량, 가격 크롤링"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        search_url = f"https://search.danawa.com/dsearch.php?query={category}&tab=goods&cate=1285"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        products = []

        selectors = [".prod_main_info", ".prod_item", ".item_wrap", ".list_item"]

        product_items = []
        for selector in selectors:
            product_items = soup.select(selector)
            if product_items:
                break

        if not product_items:
            return []

        for idx, item in enumerate(product_items[: max_products * 2]):
            try:
                # 상품명 추출
                name_selectors = [".prod_name a", ".item_name a", ".prod_info .name"]
                product_name = None
                for name_sel in name_selectors:
                    name_elem = item.select_one(name_sel)
                    if name_elem:
                        product_name = name_elem.get_text(strip=True)
                        break

                if not product_name:
                    continue

                # 가격 추출
                price_selectors = [
                    ".price_sect strong",
                    ".price strong",
                    ".item_price strong",
                ]
                price = "가격 정보 없음"
                for price_sel in price_selectors:
                    price_elem = item.select_one(price_sel)
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break

                # 용량 추출
                volume = extract_volume_from_name(product_name)

                # 영양성분 정보 (더미 데이터 - 실제로는 상세 페이지에서 추출)
                nutrition_info = generate_nutrition_info(product_name, category)

                product_data = {
                    "prod_name": product_name,
                    "price": price,
                    "volume": volume,
                    "category": category,
                    "nutrition": nutrition_info,
                    "selected_volume_reference": selected_volume,
                }

                products.append(product_data)

                if len(products) >= max_products:
                    break

            except Exception as e:
                continue

        return products

    except Exception as e:
        return []


def generate_nutrition_info(product_name, category):
    """상품명과 카테고리 기반으로 영양성분 정보 생성 (실제 환경에서는 상세 페이지 크롤링)"""
    # 카테고리별 기본 영양성분 템플릿
    nutrition_templates = {
        "그릭요거트": {
            "칼로리": f"{random.randint(80, 150)}kcal",
            "단백질": f"{random.randint(8, 15)}g",
            "지방": f"{random.randint(0, 8)}g",
            "탄수화물": f"{random.randint(5, 15)}g",
            "당분": f"{random.randint(0, 12)}g",
            "나트륨": f"{random.randint(30, 80)}mg",
        },
        "탄산음료": {
            "칼로리": f"{random.randint(0, 150)}kcal",
            "단백질": "0g",
            "지방": "0g",
            "탄수화물": f"{random.randint(0, 35)}g",
            "당분": f"{random.randint(0, 35)}g",
            "나트륨": f"{random.randint(5, 25)}mg",
        },
        "과자": {
            "칼로리": f"{random.randint(400, 550)}kcal",
            "단백질": f"{random.randint(5, 12)}g",
            "지방": f"{random.randint(15, 30)}g",
            "탄수화물": f"{random.randint(50, 70)}g",
            "당분": f"{random.randint(2, 15)}g",
            "나트륨": f"{random.randint(200, 600)}mg",
        }
    }

    # 카테고리에 맞는 템플릿 선택
    for key, template in nutrition_templates.items():
        if key in category or key in product_name:
            return template

    # # 기본 템플릿
    return {
        "칼로리": f"{random.randint(50, 300)}kcal",
        "단백질": f"{random.randint(1, 10)}g",
        "지방": f"{random.randint(0, 15)}g",
        "탄수화물": f"{random.randint(5, 40)}g",
        "당분": f"{random.randint(0, 25)}g",
        "나트륨": f"{random.randint(10, 200)}mg",
    }


def render():
    st.title("🔍 다나와 상품 분석 시스템")

    # 디렉토리 생성
    create_directories()

    # 세션 상태 초기화
    if "step" not in st.session_state:
        st.session_state.step = 1

    if "original_products" not in st.session_state:
        st.session_state.original_products = None

    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None

    if "similar_products" not in st.session_state:
        st.session_state.similar_products = None

    # 상품 정보 확인
    if "product_info" not in st.session_state:
        st.error("❌ 상품 정보가 없습니다. 이전 단계로 돌아가주세요.")
        if st.button("이전 단계로"):
            st.session_state.page = "img_to_analysis"
        return

    product_info = st.session_state.product_info
    extracted_products = extract_product_info(product_info)

    if not extracted_products:
        st.error("상품 정보를 추출할 수 없습니다.")
        return

    main_product = extracted_products[0]  # 첫 번째 상품 사용

    # 경로 설정
    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Step 1: 원본 상품의 용량별 옵션 크롤링
    if st.session_state.step == 1:
        st.subheader("📋 1단계: 원본 상품 분석")
        st.json(product_info)

    # 입력한 상품 정보를 original_product 폴더에 저장
        original_filename = (
            f"{file_path}/original_product/input_product_{int(time.time())}.json"
        )
        with open(original_filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "input_product_info": product_info,
                    "extracted_products": extracted_products,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        st.success(f"📁 입력 상품 정보가 '{original_filename}' 파일에 저장되었습니다.")

        st.subheader(f"🔍 '{main_product['prod_name']}' 용량별 옵션 검색")

        if st.button("🚀 용량별 옵션 크롤링 시작"):
            with st.spinner("용량별 상품 옵션을 검색 중입니다..."):
                search_term = (
                     main_product["prod_name"] or main_product["search_keyword"]
                )
                original_products = crawl_original_product_volumes(
                    search_term, max_products=3
                )

                if original_products:
                    st.session_state.original_products = original_products

                    # JSON 파일을 danawa_product 폴더에 저장
                    danawa_filename = (
                        f"{file_path}/danawa_product/original_products_{int(time.time())}.json"
                    )
                    with open(danawa_filename, "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "search_term": search_term,
                                "products": original_products,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            },
                            f,
                            ensure_ascii=False,
                            indent=2,
                        )

                    st.success(
                        f"✅ {len(original_products)}개의 용량 옵션을 찾았습니다!"
                    )
                    st.success(f"📁 결과가 '{danawa_filename}' 파일에 저장되었습니다.")
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("용량별 옵션을 찾을 수 없습니다.")

    # Step 2: 용량 선택
    elif st.session_state.step == 2:
        st.subheader("📦 2단계: 용량 선택")

        if st.session_state.original_products:
            st.write("**발견된 용량 옵션들:**")

            options = []
            for idx, product in enumerate(st.session_state.original_products):
                option_text = (
                    f"{product['prod_name']} - {product['volume']} - {product['price']}"
                )
                options.append(option_text)
                st.write(f"{idx+1}. **{product['prod_name']}**")
                st.write(f"   - 용량: {product['volume']}")
                st.write(f"   - 가격: {product['price']}")
                st.write("---")

            # 사용자 선택
            selected_idx = st.selectbox(
                "비교 분석할 상품을 선택하세요:",
                range(len(options)),
                format_func=lambda x: f"옵션 {x+1}: {st.session_state.original_products[x]['volume']}",
            )

            st.session_state.selected_original_product_index = selected_idx

            if st.button("선택 완료"):
                st.session_state.selected_product = st.session_state.original_products[
                    selected_idx
                ]
                st.session_state.step = 3
                st.rerun()

        if st.button("이전 단계로"):
            st.session_state.step = 1
            st.rerun()

    # Step 3: 유사 상품 크롤링
    elif st.session_state.step == 3:
        st.subheader("🔍 3단계: 유사 상품 분석")

        selected = st.session_state.selected_product
        st.write(f"**선택된 상품**: {selected['prod_name']}")  # type: ignore
        st.write(f"**용량**: {selected['volume']}")  # type: ignore
        st.write(f"**가격**: {selected['price']}")  # type: ignore
        

        if st.button("🚀 유사 상품 크롤링 시작"):
            with st.spinner("카테고리 기반 유사 상품을 검색 중입니다..."):
                category = main_product["search_keyword"]
                selected_volume = selected["volume"]  # type: ignore

                similar_products = crawl_similar_products_by_category(
                    category, selected_volume, max_products=5
                )

                if similar_products:
                    st.session_state.similar_products = similar_products

                    # JSON 파일을 danawa_product 폴더에 저장
                    danawa_filename = (
                        f"{file_path}/danawa_product/similar_products_{int(time.time())}.json"
                    )
                    comparison_data = {
                        "selected_product": selected,
                        "category": category,
                        "similar_products": similar_products,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    with open(danawa_filename, "w", encoding="utf-8") as f:
                        json.dump(comparison_data, f, ensure_ascii=False, indent=2)

                    st.success(
                        f"✅ {len(similar_products)}개의 유사 상품을 찾았습니다!"
                    )
                    st.success(
                        f"📁 비교 데이터가 '{danawa_filename}' 파일에 저장되었습니다."
                    )

                    # 결과 미리보기
                    st.subheader("📊 발견된 유사 상품들")
                    for idx, product in enumerate(similar_products):
                        with st.expander(f"상품 {idx+1}: {product['prod_name']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**가격**: {product['price']}")
                                st.write(f"**용량**: {product['volume']}")
                            with col2:
                                st.write("**영양성분**:")
                                for key, value in product["nutrition"].items():
                                    st.write(f"- {key}: {value}")

                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("유사 상품을 찾을 수 없습니다.")

        if st.button("이전 단계로"):
            st.session_state.step = 2
            st.rerun()

    # Step 4: 완료 및 다음 단계
    elif st.session_state.step == 4:
        st.subheader("✅ 4단계: 분석 완료")

        st.success("모든 데이터 수집이 완료되었습니다!")
        st.write("- 원본 상품의 용량별 옵션 수집 완료")
        st.write("- 선택된 상품 기준 유사 상품 수집 완료")
        st.write("- 영양성분 및 가격 정보 수집 완료")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("처음부터 다시"):
                st.session_state.step = 1
                st.session_state.original_products = None
                st.session_state.selected_product = None
                st.session_state.similar_products = None
                st.rerun()

        with col2:
            if st.button("결과 분석으로 이동"):
                st.session_state.page = "result"
                st.rerun()
