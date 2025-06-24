import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. OCR 모델 초기화
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='korean',
    use_gpu=False,
    det_db_thresh=0.3,
    det_db_box_thresh=0.4,
    det_db_unclip_ratio=1.6,
    drop_score=0.3,
    show_log=False
)

# 2. 이미지 경로 설정
img_path = '../assets/raw/example2.png' 
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 한글 폰트 경로 (Windows 기준)

# 3. 이미지 로드 및 색상 변환
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {img_path}")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# 4. OCR 수행
result = ocr.ocr(img_path, cls=True)

# 5. 결과 추출
res = result[0]  # 첫 번째 이미지 결과
boxes = [line[0] for line in res]
texts = [line[1][0] for line in res]
scores = [float(line[1][1]) for line in res]

# 6. 결과 출력
print(f"\n감지된 텍스트 {len(texts)}개")
for i, (text, score) in enumerate(zip(texts, scores), 1):
    print(f"{i:2d}: {text:30s} (신뢰도: {score:.3f})")

# 7. 시각화 및 저장
plt.figure(figsize=(16, 16))
annotated = draw_ocr(img_rgb, boxes, texts, scores, font_path=font_path)
plt.imshow(annotated)
plt.axis('off')
plt.title('OCR 결과')
plt.show()

# 8. 이미지 저장
result_img = Image.fromarray(annotated)
result_img.save('result.jpg')