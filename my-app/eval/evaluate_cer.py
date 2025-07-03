import json
import re
import unicodedata

# 정규화 함수
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w가-힣]", "", text)
    return text.lower()

# 한 글자라도 포함되면 해당 글자 정답으로 간주
def inclusion_cer(gt_text, pred_text):
    gt_text = normalize_text(gt_text)
    pred_text = normalize_text(pred_text)

    if not gt_text:
        return 0.0  # GT 없음이면 에러율 0으로 처리

    match = sum(1 for c in gt_text if c in pred_text)
    return 1 - (match / len(gt_text))

# 파일 경로
gt_path = "my-app/ground_truth/gt_labels.json"
pred_path = "my-app/results/merged_result.json"

# 정답 및 예측 결과 불러오기
with open(gt_path, encoding="utf-8") as f:
    gt_list = json.load(f)

with open(pred_path, encoding="utf-8") as f:
    pred_list = json.load(f)

filename_to_pred = {d["filename"]: d for d in pred_list}
cers = []

for item in gt_list:
    filename = item["filename"]
    gt_text = item.get("gt_text", "").strip()

    pred = filename_to_pred.get(filename)
    if not pred:
        print(f"{filename} 결과 없음")
        continue

    pred_text = pred.get("ocr_text", "").strip()

    if not pred_text:
        print(f"⚠️ {filename} 예측 텍스트 없음")
        continue

    score = inclusion_cer(gt_text, pred_text)
    cers.append(score)

# 결과 출력
if cers:
    avg_cer = sum(cers) / len(cers)
    print(f"✅ 평균 CER (Character Error Rate): {avg_cer:.4f}")
else:
    print("CER 계산을 위한 유효한 비교 쌍이 없습니다.")
