import json
import os
import google.generativeai as genai 
from dotenv import load_dotenv
import re
#load_dotenv()

#GOOGLE_API_KEY = "AIzaSyAI9IAitYa1-kEreg_g959aSPOXgaglSfo"
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

genai.configure(api_key="AIzaSyAI9IAitYa1-kEreg_g959aSPOXgaglSfo")

# def get_product_info_from_ocr(ocr_text_list, save_path='my-app/data/llm_info.json'):
#     prompt = f"""
#     아래는 OCR로 인식한 식품 포장지의 텍스트입니다.
#     이 내용을 바탕으로 아래 항목을 포함한 JSON을 생성해주세요:

#     - product_name: 제품의 정식 명칭
#     - product_type: 이 제품이 속하는 카테고리 또는 상품 종류 (예: 제로 음료, 그릭요거트 등)
#     - search_keyword: 다나와 검색을 위한 키워드. product_type과 total_weight를 조합해서 생성 (예: "그릭요거트 100g")

#     텍스트: {ocr_text_list}
#     """

#     model = genai.GenerativeModel('gemini-2.0-flash')
#     response = model.generate_content(prompt)
#     content = response.text.strip()

#     # >>> JSON 블록만 추출 <<<
#     json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
#     if json_match:
#         json_str = json_match.group(1).strip()
#     else:
#         # JSON 태그가 없을 경우 대안 처리
#         json_match = re.search(r'(\{.*\})', content, re.DOTALL)
#         if json_match:
#             json_str = json_match.group(1).strip()
#         else:
#             raise ValueError("JSON 응답 블록을 찾을 수 없습니다:\n" + content)
        
#     # >>> 파싱 및 저장 <<<
#     try:
#         json_data = json.loads(json_str)
#     except:
#         raise ValueError("JSON 파싱 오류:\n" + json_str)

#     with open(save_path, 'w', encoding='utf-8') as f:
#         json.dump(json_data, f, ensure_ascii=False, indent=2)

#     return json_data



def get_product_info_from_ocr(ocr_text_list, save_path='my-app/data/llm_info.json'):
        prompt = f"""
        아래는 OCR로 인식된 텍스트 토큰들의 나열입니다.  
        토큰에는 오타, 띄어쓰기 오류, 불완전한 부분이 있을 수 있습니다.  
        이 토큰들을 바탕으로, 실제로 시중에 존재하는 식품 제품의 정식 제품명과 제조사(브랜드명), 그리고 제품 유형을 추출해 주세요

        - product_name: 시장에 실제 판매되는 정확한 제품명  
        - company_name: 해당 제품을 제조·판매하는 회사나 브랜드  
        - product_type: 제품 분류 (예: 과자, 음료, 소스 등)
        - search_keyword: 다나와 검색용 키워드 (제품명 기반)

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
        model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
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
            m = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if m:
                json_block = m.group(1)
            else:
                # 3) 중괄호 객체들만 찾아서 배열로 감싸기
                objs = re.findall(r'\{[^{}]*\}', content, re.DOTALL)
                if objs:
                    json_block = objs[0]
                else:
                    # 파싱할 수 있는 블록이 전혀 없을 때
                    json_block = '{}'

            # 4) 파싱
            try:
                data_obj = json.loads(json_block)
            except json.JSONDecodeError as e:
                # 최후의 안전장치: 빈 딕셔너리
                print(f"[경고] JSON 파싱 실패: {e}\n원본 응답:\n{content}")
                data_obj = {}

        # 5) 파일로 저장 (전체 객체)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data_obj, f, ensure_ascii=False, indent=2)

        return data_obj