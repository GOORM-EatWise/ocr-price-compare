import os, cv2, json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr

def run_ocr(img_path: str, font_path: str, save_path: str = '../data/ocr_result.json'):
    ocr = PaddleOCR(
        use_angle_cls=True, lang='korean',
        det_db_thresh=0.3, det_db_box_thresh=0.4,
        det_db_unclip_ratio=1.6, drop_score=0.3, show_log=False
    )

    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"이미지 없음: {img_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = ocr.ocr(img_path, cls=True)

    res = result[0]
    boxes = [line[0] for line in res]
    texts = [line[1][0] for line in res]
    scores = [float(line[1][1]) for line in res]

    # 결과 저장 (JSON)
    ocr_json = [{"text": t, "score": s} for t, s in zip(texts, scores)]
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(ocr_json, f, ensure_ascii=False, indent=2)

    # 시각화 저장
    annotated = draw_ocr(img_rgb, boxes, texts, scores, font_path=font_path)
    result_img = Image.fromarray(annotated)
    result_img.save(os.path.join(os.path.dirname(save_path), 'ocr_annotated.jpg'))

    return ocr_json
