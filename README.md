# 🎯 프로젝트 소개

## 1. 프로젝트 개요

**ESL(전자 가격표)** 를 촬영하면 **OCR**로 상품명·제조사·가격 정보를 자동 추출하고, **LLM(Gemini API)** 로 정제한 데이터와 **영양정보(칼로리, 당, 단백질, 지방, 나트륨)** 를 결합하여 **다나와·쿠팡·이마트** 등 주요 유통 채널의 온라인 가격과 비교·시각화하는 **마트 상품 정보·가격 비교 플랫폼**입니다.

---

## 1.1. 개발배경 및 필요성

* 복잡한 영양성분표는 작은 글씨로 가독성이 떨어지고, 소비자는 여러 제품을 일일이 비교하기 번거로움
* 온라인·오프라인 채널마다 정보 형식이 달라, 앱·웹 전환을 통한 비교가 비효율적
* 건강 중시 트렌드에 따라 영양소 비교 수요 증가, 자동화된 정보 제공 시스템 필요

---

## 1.2. 개발 목표 및 주요 내용

**목표**

* 마트 전자 가격표 사진 촬영만으로 핵심 영양소(칼로리, 당, 단백질, 지방, 나트륨) 추출
* JSON 형태로 정제된 영양성분 정보 제공
* 유통 채널별 실시간 가격 비교 및 차트 시각화

**주요 내용**

1. **이미지 전처리**: 회전 보정, 노이즈 제거 (OpenCV)
2. **OCR 수행**: PaddleOCR, EasyOCR 벤치마킹 후 최적 모델 선택
3. **영양소 파싱**: 정규표현식 + Gemini API로 JSON 구조화
4. **가격 크롤링**: BeautifulSoup/requests 기반 다나와 API 연동
5. **UI/UX**: Streamlit 웹 대시보드

---

## 1.3. 세부 시나리오

> **김철수 시나리오**
>
> 1. 바디프로필 준비를 위해 칼로리 대비 단백질 함량 높은 제품 검색
> 2. EatWise 앱에서 ESL(전자 가격표) 사진 촬영
> 3. OCR→LLM 후처리 후 JSON 결과 확인
> 4. 유사 제품 비교 차트로 최적 제품 선택
> 5. 선택 제품 최저가 구매 링크 제공

---

## 1.4. 기존 서비스 대비 차별성

| 구분    | 기존 서비스     | 본 플랫폼           |
| ----- | ---------- | --------------- |
| 비교 방식 | 상품명 키워드 검색 | 촬영 기반 자동 OCR 비교 |
| 정확도   | OCR 단독 처리  | OCR+LLM 결합 구조화  |
| 채널    | 단일 이커머스    | 다채널(다나와) |
| UI    | 텍스트 리스트    | 테이블·차트 시각화      |

---

# 2. 상세 설계

## 2.1. 시스템 구성도
![image](https://github.com/user-attachments/assets/ba26d875-d55a-4389-9904-0a73db71764e)


> 프론트(UI) ⇄ 백엔드(API) ⇄ LLM 서비스 ⇄ DB ⇄ OCR·크롤링 모듈

## 2.2. 사용자 플로우 차트
![image](https://github.com/user-attachments/assets/641e649d-0c2b-4532-97e9-8884e6aec411)

## 2.3. 사용 기술

| 영역      | 기술·버전                             |
| ------- | --------------------------------- |
| OCR·전처리 | Python3.10, OpenCV, PaddleOCR     |
| AI·구조화  | Gemini API (Gemini-2.0-flash)     |
| 크롤링     | BeautifulSoup, requests           |
| 백엔드     | FastAPI                           |
| 프론트엔드   | Streamlit1.25.0|
| DB      | FireBase                      |

---

# 3. 개발 결과

## 3.1. 전체 시스템 흐름도
![image](https://github.com/user-attachments/assets/744098a1-6aa5-43e2-8c78-3f8a86a00105)

1. 이미지 업로드/촬영 → 2. 전처리 → 3. OCR → 4. 구조화 → 5. 가격 크롤링 → 6. 시각화 → 7. 히스토리 저장

## 3.2. 데이터베이스 명세서

**주요 테이블**
![image](https://github.com/user-attachments/assets/e3089331-43d3-4ac8-b973-6cbce138754d)

|          테이블명          | 컬럼                                                                                            | 설명                         |
| :--------------------: | :-------------------------------------------------------------------------------------------- | :------------------------- |
|        **users**       | id (PK), email, password\_hash, created\_at                                                   | 사용자 계정 정보 관리               |
|        **files**       | file\_id (PK), user\_id (FK), name, type, create\_at                                          | 앱으로 저장된 파일 관리              |
|   **product\_images**  | prod\_id (FK), file\_id (FK)                                                                  | 식별된 상품 이미지 매핑              |
|    **product\_cat**    | cat\_id (PK), name, keyword                                                                   | LLM 생성 카테고리 관리 및 검색 키워드 저장 |
|    **product\_info**   | prod\_id (PK), cat\_id (FK), prod\_name, price, per\_serving, kcal, carb, sugar, protein, fat | 상품 기본 정보 및 영양성분            |
| **price\_comparisons** | scan\_id (FK), prod\_id (FK), price, channel                                                  | 유통 채널별 가격 비교 결과            |

## 3.3. 기능 설명

### 3.3.1. OCR 실행 페이지

* **기능**: 이미지 업로드/촬영 → ROI 자동 탐지 → OCR 진행
* **UI**: 원본 이미지, 추출 텍스트 대조 화면

### 3.3.2. 영양정보 비교 대시보드

* **기능**: JSON 데이터 테이블 표시
* **시각화**: 용량 정규화 막대그래프, 평균·최저값 강조


## 3.4. 디렉토리 구조

```text
ocr-price-compare/
│
├── .venv/                        # Python 가상환경 (버전관리에서 제외)
├── .gitignore                    # Git 추적 제외 파일 목록
├── requirements.txt              # 프로젝트 전체 의존성 정의
├── README.md                     # 프로젝트 설명
├── UI_WorkFlow.png               # UI 워크플로우(디자인)
├── my-app/                            # 실제 애플리케이션 코드
│		│
│		├── main_page.py                   # 메인 애플리케이션 진입점
│		├── run_all_ocr_llm.py             # 분류 성능 평가
│		├── 📁 analysis_results            # 정적 자원 및 샘플 파일
│   ├── 📁 annotated                   #OCR 인식 확인 이미지
│		│   ├── annotated.jpg
│   ├── 📁 annotated_proc              #OCR 인식 확인 이미지(전처리 적용)
│		│   ├── annotated.jpg
│		│
│		├── 📁 danawa_product/             # 다나와 크롤링 상품 정보 저장
│		│   ├── original_products_{}.json  # OCR 추출 결과 데이터
│		│   └── similar_products_{}.json   # 시각화된 OCR 결과 이미지
│		│
│		├── 📁 data/                      # OCR 인식 확인 이미지(추출 결과 산출용)
│		│   ├── 📁 annotated              
│		│   │     ├──annotated_orig.jpg
│		│   │     └──annotated_proc.jpg
│		│   ├── 📁 ocr
│		│        ├──ocr_result_orig.jpg
│		│        └──ocr_result_proc.jpg
│		├── 📁 db/                       # db 연결
│		│   ├──README.md                  # db 사용 설명(key 관련)
│		│   └──gitkeep.txt
│		│
│		├── 📁 eval/                        # OCR 성능평가
│		│   ├──common.py                
│		│   ├──evalutate_cer.py 
│		│   └──evaluate_info.py
│		│
│		├── 📁 ground_truth/                # 성능 평가용(라벨)
│		│   └── gt_labels.json                            
│		│
│		├── 📁 json/                        # ocr 결과 저장
│   │   ├── README.md  
│		│   └── ocr_result.json           
│		│
│		├── 📁 json_proc/                   # ocr 결과 저장(전처리 적용)
│   │   ├── README.md  
│		│   └── ocr_result.json   
│		│
│		├── 📁 llm/                        # llmtext 분류 함수
│   │   ├── README.md  
│		│   └── promt_to_json.py
│		│
│		├── 📁 llm_json/                    # text 분류 결과 저장
│   │   ├── README.md  
│		│   └── llm_result.json
│		│
│		├── 📁 ocr/                        # ocr 모듈
│		│   └── paddle_ocr.py          
│		│
│		├── 📁 original_product/             # 원상품 크롤링 결과 저장
│		│   └── input_product_{}.json        
│		│
│		├── 📁 pages/                        # page들 구성
│		│   ├── README.md
│		│   ├── camera.py
│		│   ├── crawling.py
│		│   ├── db.py
│		│   ├── eatwise_info.py
│		│   ├── get_user_info.py
│		│   ├── image_upload.py
│		│   ├── image_upload_option.py
│		│   ├── image_to_analysis.py
│		│   └── result.py
│		│
│		├── 📁 preprocessing/                 #이미지 전처리 모듈
│		│   └── README.md                     # 결과 데이터 저장 관리
│		│   └── preprocess.py        
│		│
│		└── 📁 results/                         # 성능평가용 결과 합
│		│    └── merged_result.json               
│		│
│		├── 📁 sample/                       # 데이터 샘플
│		│    └── IMG_8285.jpg
│		│
│		├── 📁 thumbnails/                    #UI 썸네일용
│		│    ├── EatWise_logo.png
│		│    └── sample.jpg
│		│
│		├── 📁 utilss/                        #util 모듈
│		│    ├── __init__.py
│		│    └── ocr_utils.py
```

---

# 4. 설치 및 사용 방법

1. 클론 & 가상환경 설정

   ```bash
   git clone https://github.com/YourOrg/ocr-price-compare.git
   cd ocr-price-compare
   python -m venv .venv
   source .venv/bin/activate
   ```
2. 의존성 설치

   ```bash
   pip install -r requirements.txt
   ```
3. 환경변수 설정

   ```bash
   cp .env.example .env
   # GOOGLE_API_KEY, CHANNEL_API_KEYS 등 입력
   ```
4. 앱 실행

   ```bash
   streamlit run my-app/main_page.py  # 웹 UI
   ```

---

# 5. 소개 및 시연 영상

> [시연 영상 보러가기](https://youtu.be/2g-vNY3k8fw)

---

# 6. 팀 소개

| 이름  | 역할           | 연락처                                                     |
| --- | ------------ | ------------------------------------------------------- |
| 김지웅 | 팀장·UI/UX·기획  | [nomeanness12@naver.com](mailto:nomeanness12@naver.com)   |
| 강요셉 | 데이터 수집·크롤링   | [hwankkot@outlook.com](mailto:hwankkot@outlook.com) |
| 안소희 | AI OCR 모델 개발 | [soheean1370@gmail.com](soheean1370@gmail.com)     |
| 김수언 | 시각화, 인사이트·리포트     | [sueon1989@gmail.com](mailto:sueon1989@gmail.com)   |

---

# 7. 해커톤 참여 후기

> **김지웅**: 협업을 통해 OCR 파이프라인 최적화 경험
>
> **강요셉**: 실시간 데이터 크롤링 모듈 개발로 성장
>
> **안소희**: LLM 연동 정제 과정에서 기술 역량 향상
>
> **김수언**: 데이터 시각화·보고서 작성 능력 강화
