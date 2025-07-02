# utils/ocr_utils.py
import re

def ocr_quality_score(ocr_json):
    full_text = " ".join([item['text'] for item in ocr_json if item['text']])
    if not full_text:
        return 0

    # 1) 길이 기반 점수 (최대 1.0)
    length_score = min(len(full_text) / 100, 1.0)

    # 2) 노이즈 비율 계산
    allowed_punct = set(".!?,%-:()/")
    non_alnum = 0
    for c in full_text:
        if not (c.isalnum() or c.isspace() or c in allowed_punct):
            non_alnum += 1
    noise_ratio = non_alnum / max(len(full_text), 1)
    noise_score = max(0, 1 - noise_ratio * 2)

    # 3) 단어 길이 정상 여부
    words = re.findall(r'\S+', full_text)
    if words:
        avg_len = sum(len(w) for w in words) / len(words)
        word_len_score = 1.0 if 1.5 <= avg_len <= 12 else 0.5
    else:
        word_len_score = 0

    # 4) 한글·영문·숫자 비율
    hangul = len(re.findall(r'[가-힣]', full_text))
    eng_num = len(re.findall(r'[A-Za-z0-9]', full_text))
    lang_score = min((hangul + eng_num) / max(len(full_text),1) * 1.5, 1.0)

    # 최종 점수
    return length_score * noise_score * word_len_score * lang_score
