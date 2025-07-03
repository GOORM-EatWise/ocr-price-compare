import os
import cv2
import json
from glob import glob
from ocr.paddle_ocr import run_ocr  # 실제 모듈 이름에 맞게 수정
from llm.promt_to_json import get_product_info_from_ocr


# 입력 이미지 폴더
image_dir = "my-app/assets/best"
# 출력 JSON 경로
output_path = "my-app/results/merged_result.json"

font_path = 'C:/Windows/Fonts/malgun.ttf'
# 누적 결과 리스트
all_results = []

# 이미지 리스트 가져오기 (png, jpg 지원)
image_files = sorted(glob(os.path.join(image_dir, "*.png")) + glob(os.path.join(image_dir, "*.jpg")))

for img_path in image_files:
    filename = os.path.basename(img_path)
    print(f"🔍 Processing {filename} ...")

    # 이미지 읽기
    img = cv2.imread(img_path)
    if img is None:
        print(f"{filename} 읽기 실패")
        continue

    # OCR 실행
    ocr_data, _ = run_ocr(img, font_path)

    text_list = [d["text"] for d in ocr_data]
    ocr_text = " ".join(text_list)
    product_info = get_product_info_from_ocr(ocr_text)

    status = "NO" if any(v is None for v in product_info.values()) else "OK"

    result = {
    "filename": filename,
    "status": status,
    "product_info": product_info,
    "ocr_text": ocr_text  # 여기에 OCR 전체 텍스트 저장!
}
    all_results.append(result)


# 5. 저장
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n✅ 모든 결과 저장 완료: {output_path}")
