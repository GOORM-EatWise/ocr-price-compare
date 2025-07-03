import cv2
import numpy as np

def preprocess_image(img: np.array):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)




def detect_and_draw_rectangles(img: np.array, block_size=15, C=5,
                               morph_kernel=(3, 3),
                               min_area_ratio=0.003,
                               draw_result=False):

    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    bw = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,  
        block_size, C
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel)
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=1)

    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for cnt in cnts:
        x, y, ww, hh = cv2.boundingRect(cnt)
        area = ww * hh
        aspect = ww / float(hh + 1e-5)

        if area >= w * h * min_area_ratio and 0.8 < aspect < 5.0 and hh > 30:
            rects.append((x, y, ww, hh))
    
    cropped_images = [img[y:y + hh, x:x + ww] for (x, y, ww, hh) in rects]
    
    return rects, cropped_images