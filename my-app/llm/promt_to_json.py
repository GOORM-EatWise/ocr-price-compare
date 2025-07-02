import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

current_path = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(current_path, ".env"))

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)  # type: ignore


def get_product_info_from_ocr(
    ocr_text_list,
    save_path="my-app/data/llm_info.json",
):

    prompt = f"""
        아래는 OCR로 인식된 텍스트 토큰들의 나열입니다.
        토큰에는 오타, 띄어쓰기 오류, 불완전한 부분이 있을 수 있습니다.
        이 토큰들을 바탕으로, 실제로 시중에 존재하는 식품 제품의 정식 제품명과 제조사(브랜드명), 그리고 제품 유형을 추출해 주세요

        - product_name: 시장에 실제 판매되는 정확한 제품명
        - company_name: 해당 제품을 제조·판매하는 회사나 브랜드
        - product_type: 제품 분류 (예: 과자, 음료, 소스 등)
        - search_keyword: 제품과 유사한 제품들을 찾을 수 있는 키워드 (예: 풀무원 그릭 요거트 → 그릭요거트)

        **요구 사항**
        1. OCR 오류로 인한 무의미한 토큰은 제거하고,
        2. 띄어쓰기·철자 오류를 교정하여 실제 이름으로 작성하며,
        3. `(추정)` 등의 애매한 표시 없이, 최대한 확실한 이름으로 응답합니다.
        4. 반드시 JSON 객체 하나만 출력해주세요.
        5. 코드 블록이나 추가 설명 없이, 순수 JSON만 내보내야 합니다.

            예시:
            {{
            "product_name": "그릭요거트 플레인",
            "company_name": "매일유업",
            "product_type": "요거트",
            "search_keyword": "그릭요거트"
            }}

        텍스트: {ocr_text_list}
        """
    model = genai.GenerativeModel("models/gemini-2.0-flash-lite")  # type: ignore
    response = model.generate_content(prompt)
    content = response.text.strip()

    # 1) 응답 전체가 JSON 배열/객체일 경우 바로 파싱 시도
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        data_obj = parsed
    elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
        data_obj = parsed[0]
    else:
        # 2) ```json ... ``` 블록 내부 추출
        m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if m:
            json_block = m.group(1)
        else:
            # 3) 중괄호 객체들만 찾아서 배열로 감싸기
            objs = re.findall(r"\{[^{}]*\}", content, re.DOTALL)
            if objs:
                json_block = objs[0]
            else:
                # 파싱할 수 있는 블록이 전혀 없을 때
                json_block = "{}"

        # 4) 파싱
        try:
            data_obj = json.loads(json_block)
        except json.JSONDecodeError as e:
            # 최후의 안전장치: 빈 딕셔너리
            print(f"[경고] JSON 파싱 실패: {e}\n원본 응답:\n{content}")
            data_obj = {}

    # 5) 파일로 저장 (전체 객체)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data_obj, f, ensure_ascii=False, indent=2)

    return data_obj
