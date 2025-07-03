import json
import re
import unicodedata

# 텍스트 정규화 함수: 한글 자소 결합 + 특수문자 제거 + 소문자
def normalize(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w가-힣]", "", text)
    return text.lower()

# 부분 포함 판단 (한 글자라도 포함)
def is_partial_match(gt, pred):
    gt = normalize(gt)
    pred = normalize(pred)
    return any(c in pred for c in gt) if gt and pred else False

# 데이터 로딩
with open("my-app/ground_truth/gt_labels.json", encoding="utf-8") as f:
    gt_list = json.load(f)

with open("my-app/results/merged_result.json", encoding="utf-8") as f:
    pred_list = json.load(f)

filename_to_pred = {d["filename"]: d for d in pred_list}

tp, fp, fn = 0, 0, 0

for item in gt_list:
    filename = item["filename"]
    gt_info = item["product_info"]
    pred = filename_to_pred.get(filename)

    if not pred:
        print(f"{filename} 결과 없음")
        continue

    pred_info = pred["product_info"]

    for key in ["product_name", "company_name", "product_type"]:
        gt_value = gt_info.get(key)
        pred_value = pred_info.get(key)

        if pred_value is None:
            if gt_value is not None:
                fn += 1
        elif gt_value is None:
            fp += 1
        elif is_partial_match(gt_value, pred_value):
            tp += 1
        else:
            fp += 1
            fn += 1

# 지표 계산
precision = tp / (tp + fp) if tp + fp > 0 else 0
recall = tp / (tp + fn) if tp + fn > 0 else 0
f1_score  = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0


print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall   : {recall:.4f}")
print(f"✅ F1-score : {f1_score:.4f}")