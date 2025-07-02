import os, cv2, json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr

def run_ocr(img: np.array, font_path: str, save_json: str = None, save_annotated: str = None):
    """
    - img_path: 입력 이미지
    - font_path: draw_ocr 시 사용할 한글 폰트 경로
    - save_json: OCR 결과(JSON)를 저장할 경로 (None이면 저장 안 함)
    - save_annotated: 박스 그린 이미지를 저장할 경로 (None이면 저장 안 함)
    Returns: ocr_data (list of dict), annotated_image (numpy array RGB)
    """
    # 1OCR 초기화 
    ocr = PaddleOCR(use_angle_cls=True, lang='korean', use_gpu=False,show_log=False)

    # 이미지 읽고 RGB 변환
    #img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError("이미지 없음")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # OCR 수행
    result = ocr.ocr(img_rgb, cls=True)[0]

    # 텍스트·스코어·박스 추출
    boxes, texts, scores = [], [], []
    for box, (txt, sc) in result:
        boxes.append(box)
        texts.append(str(txt))
        scores.append(float(sc))

    # JSON 형태로 묶기
    ocr_data = [{"text": t, "score": s, "box": b} for t, s, b in zip(texts, scores, boxes)]

    # JSON 저장
    if save_json:
        os.makedirs(os.path.dirname(save_json), exist_ok=True)
        with open(save_json, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, ensure_ascii=False, indent=2)

    # 시각화 (draw_ocr returns RGB array)
    annotated = draw_ocr(img_rgb, boxes, texts, scores, font_path=font_path)

    # Annotated 이미지 저장
    if save_annotated:
        os.makedirs(os.path.dirname(save_annotated), exist_ok=True)
        Image.fromarray(annotated).save(save_annotated)

    return ocr_data, annotated