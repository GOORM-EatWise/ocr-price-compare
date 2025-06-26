import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# 한글 폰트 사용하기
# !pip install koreanize-matplotlib
import koreanize_matplotlib         # 한글 사용 패치 import


# JSON 형식의 영양성분 데이터 입력
product_json = {
    "product_name": "소와나무 생크림 요거트",
    "total_weight": "85g",
    "calories": "135kcal",
    "nutrition": {
        "나트륨": "53mg",
        "탄수화물": "13g",
        "당류": "12g",
        "지방": "8g",
        "트랜스지방": "1g",
        "포화지방": "5g",
        "콜레스테롤": "24mg",
        "단백질": "3g"
    },
    "nutrition_base": "100g당",
    "product_type": "요거트",
    "search_keyword": "요거트"
}

# 비교제품 데이터 생성1
compare_json1 = {
    "product_name": "요플레 오리지널 복숭아",
    "total_weight": "85g",
    "calories": "88kcal",
    "nutrition": {
        "나트륨": "71mg",
        "탄수화물": "12g",
        "당류": "19g",
        "지방": "3g",
        "트랜스지방": "0g",
        "포화지방": "2g",
        "콜레스테롤": "18mg",
        "단백질": "4g"
    },
    "nutrition_base": "100g당",
    "product_type": "요거트",
    "search_keyword": "요거트"
}

# 비교제품 데이터 생성2
compare_json2 = {
    "product_name": "바이오 요거트 (딸기&백도)",
    "total_weight": "85g",
    "calories": "76kcal",
    "nutrition": {
        "나트륨": "47mg",
        "탄수화물": "13g",
        "당류": "11g",
        "지방": "1g",
        "트랜스지방": "0g",
        "포화지방": "1g",
        "콜레스테롤": "6mg",
        "단백질": "4g"
    },
    "nutrition_base": "100g당",
    "product_type": "요거트",
    "search_keyword": "요거트"
}

# 숫자만 추출하는 함수
def extract_number(val):
    try:
        return float(''.join([c for c in val if c.isdigit() or c == '.']))
    except:
        return 0

# 데이터프레임 생성
def nutrition_to_dict(product):
    d = {k: extract_number(v) for k, v in product["nutrition"].items()}
    d["제품명"] = product["product_name"]
    return d

df = pd.DataFrame([nutrition_to_dict(product_json), nutrition_to_dict(compare_json1), nutrition_to_dict(compare_json2)])
df.set_index("제품명", inplace=True)

# 영양성분이 x축, 제품명이 범례가 되도록 전치
df_T = df.T  

# 영양성분별로 데이터 스케일 전처리 (0~1 정규화)
scaler = MinMaxScaler()
df_scaled = pd.DataFrame(
    scaler.fit_transform(df),
    columns=df.columns,
    index=df.index
)
df_scaled_T = df_scaled.T

st.title("영양성분 비교")
st.write("아래 그래프 및 표를 통해 제품별 영양성분을 비교합니다.")



## 그래프 

# st.write("그래프1. 방사형(레이더) 그래프")
categories_scaled = list(df_scaled.columns)
labels_scaled = df_scaled.index.tolist()
num_vars_scaled = len(categories_scaled)
angles_scaled = [n / float(num_vars_scaled) * 2 * 3.141592 for n in range(num_vars_scaled)]
angles_scaled += angles_scaled[:1]

fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

for idx, label in enumerate(labels_scaled):
    values = df_scaled.loc[label].tolist()
    values += values[:1]
    ax2.plot(angles_scaled, values, label=label)
    ax2.fill(angles_scaled, values, alpha=0.1)

ax2.set_xticks(angles_scaled[:-1])
ax2.set_xticklabels(categories_scaled, fontsize=14, fontweight='bold', ha='center', va='center_baseline')
ax2.tick_params(axis='x', pad=15)  # 축 레이블과 그래프 간격 조정
# plt.title("영양성분 방사형 그래프 (정규화)", fontsize=16, pad=30)
# 범례를 아래쪽으로 이동
ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=len(labels_scaled), fontsize=12)
st.pyplot(fig2)

## 데이터프레임

# # 데이터프레임1 (숫자 입력값 그대로 출력)
# st.write("데이터프레임1. 숫자만")
# def smart_format(x):
#     if isinstance(x, float) and x.is_integer():
#         return f"{int(x)}"
#     elif isinstance(x, float):
#         return f"{x}"
#     elif isinstance(x, int):
#         return f"{x}"
#     else:
#         return x

# pastel_color = "#A8FFB0"  # 밝은 연초록 (Lighter Soft Green)
# # pastel_color = "#fff9c4"  # 연노랑 (Pastel Yellow)
# st.dataframe(
#     df_T.style.format(smart_format).highlight_min(axis=1, color=pastel_color),
#     use_container_width=True    # 화면 너비에 맞게 조정
# )


# 데이터프레임2 (원본 nutrition 값으로 데이터프레임 출력)
# st.write("데이터프레임2. 원본 영양성분(단위 포함)")
df_origin = pd.DataFrame(
    [
        {**product_json["nutrition"], "제품명": product_json["product_name"]},
        {**compare_json1["nutrition"], "제품명": compare_json1["product_name"]},
        {**compare_json2["nutrition"], "제품명": compare_json2["product_name"]}
    ]
).set_index("제품명").T

pastel_color = "#A8FFB0"  # 밝은 연초록 (Lighter Soft Green)
st.dataframe(
    df_origin.style.highlight_min(axis=1, color=pastel_color),  # 영양성분 min 값 강조
    use_container_width=True                                    # 화면 너비에 맞게 조정
)




## 추가 그래프

st.write("")
st.write("")
st.write("추가 그래프")

st.write("그래프2. 막대 그래프")
fig, ax = plt.subplots(figsize=(8, 4))
df_T.plot(kind='bar', ax=ax)
# plt.ylabel("함량")
# plt.title("제품별 영양성분 비교")
plt.xticks(rotation=0)
st.pyplot(fig)

st.write("그래프3. 누적 막대 그래프")
st.bar_chart(df_T)

st.write("그래프4. 영역 차트")
st.area_chart(df_T)  # 영역 차트

st.write("그래프5. 라인 차트")
st.line_chart(df_T)  # 라인 차트

st.write("그래프6. Plotly 라인 차트")
st.plotly_chart(df_T.plot(kind='line', title=' ').get_figure())  # Plotly 라인 차트
