import json
from ocr.paddle_ocr import run_ocr
from llm.promt_to_json import get_product_info_from_ocr

img_path = 'my-app/assets/raw/example.png'
font_path =  'C:/Windows/Fonts/malgun.ttf' 

# ocr 수행
ocr_json = run_ocr(img_path, font_path, save_path='my-app/data/ocr_result.json')


# llm에 전달할 텍스트 추출
ocr_texts = [item["text"] for item in ocr_json]

# gemini로 상세 정보 추출
product_info = get_product_info_from_ocr(ocr_texts)

print("추출된 상품 상세정보:")
print(json.dumps(product_info,indent=2, ensure_ascii=False))