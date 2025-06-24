import json
import os
import google.generativeai as genai # pip install google-generativeai
from dotenv import load_dotenv
import re
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_product_info_from_ocr(ocr_text_list, save_path='my-app/data/llm_info.json'):
    prompt = f"""
    아래는 OCR로 인식한 식품 포장지의 텍스트입니다.
    이 내용을 바탕으로 아래 항목을 포함한 JSON을 생성해주세요:

    - product_name: 제품의 정식 명칭
    - total_weight: 총 용량 또는 중량 (예: 350ml, 500g)
    - calories: 총 칼로리 (예: 150kcal)
    - nutrition: 영양성분 정보 (dictionary 형식)
    - nutrition_base: 영양성분 기준량 (예: 30g 기준, 100ml 기준 등)
    - product_type: 이 제품이 속하는 카테고리 또는 상품 종류 (예: 제로 음료, 그릭요거트 등)
    - search_keyword: 다나와 검색을 위한 키워드. product_type과 total_weight를 조합해서 생성 (예: "그릭요거트 100g")

    텍스트: {ocr_text_list}
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    content = response.text.strip()

    # >>> JSON 블록만 추출 <<<
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # JSON 태그가 없을 경우 대안 처리
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            raise ValueError("JSON 응답 블록을 찾을 수 없습니다:\n" + content)
        
    # >>> 파싱 및 저장 <<<
    try:
        json_data = json.loads(json_str)
    except:
        raise ValueError("JSON 파싱 오류:\n" + json_str)

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return json_data
