import cv2
import numpy as np

def preprocess_image(img: np.array):
    #img = cv2.imread(image_path)
    
    if img is None:
        raise FileNotFoundError("이미지를 찾을 수 없습니다")

    # 1.5배 확대 (INTER_CUBIC)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE 적용 (명암 대비 향상)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # 샤프닝 필터 (경계선 강화)
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    # 저장 (이진화 없이)
    #cv2.imwrite(save_path, sharpened)
    return sharpened