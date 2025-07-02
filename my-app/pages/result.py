import streamlit as st
import re

import traceback


# 영양성분 비교 시각화(크롤링 한것 바탕으로)
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import os
from datetime import datetime

# my-app 폴더 기준 경로
BASE_DIR = os.path.dirname(__file__)            # my-app/pages/result.py 에서 불러온다면 BASE_DIR은 my-app/pages
BASE_DIR = os.path.normpath(os.path.join(BASE_DIR, '..'))  # 한 단계 위(my-app)

ORIG_DIR   = os.path.join(BASE_DIR, 'original_product')
DANAWA_DIR = os.path.join(BASE_DIR, 'danawa_product')




def extract_numeric_value(value_str):
    """문자열에서 숫자 값 추출 (예: "150kcal" -> 150)"""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    if isinstance(value_str, str):
        # 숫자만 추출
        numbers = re.findall(r'\d+(?:\.\d+)?', value_str)
        if numbers:
            return float(numbers[0])
    
    return 0.0

def normalize_nutrition_per_weight(nutrition_data, current_volume, target_weight):
    """현재 용량을 기준으로 목표 중량당 영양성분 계산"""
    # 현재 용량에서 숫자 추출
    current_weight = extract_numeric_value(current_volume)
    
    if current_weight == 0:
        current_weight = 100  # 기본값
    
    # 비율 계산
    ratio = target_weight / current_weight
    
    normalized = {}
    for key, value in nutrition_data.items():
        numeric_value = extract_numeric_value(value)
        normalized[key] = round(numeric_value * ratio, 2)
    
    return normalized

def load_saved_data():
    original_data = None
    similar_products = None

    # original_product 폴더에서 가장 최근 파일 찾기
    if os.path.isdir(ORIG_DIR):
        original_files = [f for f in os.listdir(ORIG_DIR) if f.endswith('.json')]
        if original_files:
            latest = max(
                original_files,
                key=lambda fn: os.path.getctime(os.path.join(ORIG_DIR, fn))
            )
            with open(os.path.join(ORIG_DIR, latest), 'r', encoding='utf-8') as fp:
                original_data = json.load(fp)

    # danawa_product 폴더에서 similar_products 파일 찾기
    if os.path.isdir(DANAWA_DIR):
        danawa_files = [
            f for f in os.listdir(DANAWA_DIR)
            if f.startswith('similar_products') and f.endswith('.json')
        ]
        if danawa_files:
            latest = max(
                danawa_files,
                key=lambda fn: os.path.getctime(os.path.join(DANAWA_DIR, fn))
            )
            with open(os.path.join(DANAWA_DIR, latest), 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                similar_products = data.get('similar_products', [])

    return original_data, similar_products

def create_nutrition_comparison_table_by_weight(selected_nutrients, products_data, weight):
    """특정 용량에 대한 영양성분 비교 표 생성"""
    comparison_data = []
    
    for product in products_data:
        normalized_nutrition = normalize_nutrition_per_weight(
            product['nutrition'], 
            product.get('volume', '100g'), 
            weight
        )
        
        row_data = {'제품명': product['name']}
        
        for nutrient in selected_nutrients:
            value = normalized_nutrition.get(nutrient, 0)
            
            # 단위 추가
            if nutrient == "칼로리":
                row_data[nutrient] = f"{value}kcal"
            elif nutrient in ["나트륨"]:
                row_data[nutrient] = f"{value}mg"
            else:
                row_data[nutrient] = f"{value}g"
        
        comparison_data.append(row_data)
    
    return pd.DataFrame(comparison_data)

def normalize_nutrition_for_radar(products_data, selected_nutrients):
    """영양성분 데이터를 0-1 범위로 Min-Max 정규화"""
    nutrition_df = pd.DataFrame([
        {nutrient: extract_numeric_value(product['nutrition'].get(nutrient, 0)) 
         for nutrient in selected_nutrients}
        for product in products_data
    ])
    
    # Min-Max 스케일링 적용
    normalized_df = (nutrition_df - nutrition_df.min()) / (nutrition_df.max() - nutrition_df.min())
    
    return normalized_df.fillna(0)  # NaN 값을 0으로 처리

def create_normalized_radar_chart(selected_nutrients, products_data, target_weight=30):
    """정규화된 영양성분 레이더 차트 생성"""
    
    # 용량별로 영양성분 조정
    adjusted_products = []
    for product in products_data:
        normalized_nutrition = normalize_nutrition_per_weight(
            product['nutrition'], 
            product.get('volume', '100g'), 
            target_weight
        )
        adjusted_products.append({
            'name': product['name'],
            'nutrition': normalized_nutrition
        })
    
    # Min-Max 정규화 적용
    normalized_data = normalize_nutrition_for_radar(adjusted_products, selected_nutrients)
    
    # 색상 팔레트
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    fig = go.Figure()
    
    for i, product in enumerate(adjusted_products):
        # 제품명 길이 제한
        product_name = product['name'][:15] + "..." if len(product['name']) > 15 else product['name']
        
        # 레이더 차트를 닫기 위해 첫 번째 값을 마지막에 추가
        values = normalized_data.iloc[i].values.tolist()
        values.append(values[0])
        nutrients_labels = selected_nutrients + [selected_nutrients[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=nutrients_labels,
            fill='toself',
            name=product_name,
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],  # 0-1 범위로 고정
                tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                ticktext=['최소', '20%', '40%', '60%', '80%', '최대']
            )
        ),
        showlegend=True,
        title=f"{target_weight}g 기준 정규화된 영양성분 비교",
        width=600,
        height=500,
        font=dict(size=12)
    )
    
    return fig

def get_nutrition_insights(products_data, selected_nutrients, target_weight):
    """영양성분 분석 인사이트 생성"""
    insights = []
    
    # 각 영양성분별 최고/최저 제품 찾기
    for nutrient in selected_nutrients:
        values = []
        for product in products_data:
            normalized_nutrition = normalize_nutrition_per_weight(
                product['nutrition'], 
                product.get('volume', '100g'), 
                target_weight
            )
            values.append({
                'name': product['name'],
                'value': extract_numeric_value(normalized_nutrition.get(nutrient, 0))
            })
        
        if values:
            max_product = max(values, key=lambda x: x['value'])
            min_product = min(values, key=lambda x: x['value'])
            
            if max_product['value'] != min_product['value']:
                insights.append({
                    'nutrient': nutrient,
                    'highest': max_product,
                    'lowest': min_product
                })
    
    return insights

def render():
    st.title("📊 영양성분 비교 분석 결과")
    
    # 저장된 데이터 로드
    original_data, similar_products = load_saved_data()
    
    if not original_data or not similar_products:
        st.error("❌ 분석할 데이터가 없습니다. 이전 단계에서 크롤링을 먼저 진행해주세요.")
        if st.button("크롤링 페이지로 이동"):
            st.session_state.page = 'crawling'
        return
    
    # 원본 상품 정보 추출
    original_product_info = original_data.get('input_product_info', {})
    if isinstance(original_product_info, list):
        original_product_info = original_product_info[0]
    
    # 모든 제품 데이터 준비
    products_data = []
    
    # 원본 상품 추가 (영양성분 정보가 있다면)
    if 'nutrition_info' in original_product_info:
        products_data.append({
            'name': f"입력상품: {original_product_info.get('product_name', 'Unknown')}",
            'nutrition': original_product_info['nutrition_info'],
            'volume': original_product_info.get('volume', '100g'),
            'price': original_product_info.get('price', '가격 정보 없음'),
            'type': 'original'
        })
    
    # 다나와 크롤링 상품들 추가
    for product in similar_products:
        products_data.append({
            'name': product['prod_name'],
            'nutrition': product['nutrition'],
            'volume': product['volume'],
            'price': product['price'],
            'type': 'similar'
        })
    
    if not products_data:
        st.error("비교할 제품 데이터가 없습니다.")
        return
    
    st.success(f"✅ 총 {len(products_data)}개 제품의 영양성분을 비교합니다.")
    
    # 사이드바에서 영양성분 선택
    st.sidebar.header("🎯 비교할 영양성분 선택")
    
    # 모든 제품의 영양성분 키 수집
    all_nutrients = set()
    for product in products_data:
        all_nutrients.update(product['nutrition'].keys())
    
    all_nutrients = sorted(list(all_nutrients))
    
    # 기본 선택 영양성분
    default_nutrients = []
    for nutrient in ['칼로리', '단백질', '지방', '탄수화물', '당분', '나트륨']:
        if nutrient in all_nutrients:
            default_nutrients.append(nutrient)
    
    selected_nutrients = st.sidebar.multiselect(
        "비교할 영양성분을 선택하세요:",
        all_nutrients,
        default=default_nutrients[:5] if len(default_nutrients) >= 3 else default_nutrients
    )
    
    if len(selected_nutrients) < 3:
        st.warning("⚠️ 레이더 차트를 위해 최소 3개 이상의 영양성분을 선택해주세요.")
        return
    
    # 제품 정보 미리보기
    st.subheader("📋 비교 대상 제품들")
    
    cols = st.columns(min(3, len(products_data)))
    for idx, product in enumerate(products_data):
        with cols[idx % 3]:
            with st.expander(f"📦 {product['name'][:20]}..."):
                st.write(f"**용량**: {product['volume']}")
                st.write(f"**가격**: {product['price']}")
                st.write("**영양성분**:")
                for key, value in product['nutrition'].items():
                    if key in selected_nutrients:
                        st.write(f"- **{key}**: {value}")
                    else:
                        st.write(f"- {key}: {value}")
    
    # 용량별 비교 표
    st.subheader("📊 용량별 영양성분 비교표")

    target_weights = st.multiselect(
        "비교할 용량을 선택하세요 (g):",
        [10, 20, 30, 50, 100],
        default=[10, 30, 50]
    )

    if target_weights:
        for weight in target_weights:
            st.write(f"### {weight}g 기준 영양성분 비교")
        
            comparison_df = create_nutrition_comparison_table_by_weight(
                selected_nutrients, 
                products_data, 
                weight
            )
        
            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )
        
        # 각 용량별 CSV 다운로드 버튼
            csv = comparison_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=f"📥 {weight}g 비교표 CSV 다운로드",
                data=csv,
                file_name=f"nutrition_comparison_{weight}g_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"download_{weight}g"  # 고유 키 추가
            )

            st.divider()  # 구분선 추가
    
    # 레이더 차트 
    st.subheader("🎯 영양성분 레이더 차트")

    radar_weights = st.multiselect(
        "레이더 차트로 볼 용량 선택:",
        [10, 20, 30, 50, 100],
        default=[30, 50]  # 기본값으로 2개 선택
    )

    if len(selected_nutrients) >= 3 and radar_weights:
        for weight in radar_weights:
            st.write(f"### {weight}g 기준 정규화된 레이더 차트")
        
            radar_fig = create_normalized_radar_chart(selected_nutrients, products_data, weight)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # 영양성분 분석 인사이트
            st.write("#### 📈 영양성분 분석 인사이트")
            insights = get_nutrition_insights(products_data, selected_nutrients, weight)
            
            if insights:
                insight_cols = st.columns(min(3, len(insights)))
                for idx, insight in enumerate(insights):
                    with insight_cols[idx % 3]:
                        st.info(f"""
                        **{insight['nutrient']}**
                        
                        🔺 **최고**: {insight['highest']['name'][:20]}...
                        ({insight['highest']['value']:.1f})
                        
                        🔻 **최저**: {insight['lowest']['name'][:20]}...
                        ({insight['lowest']['value']:.1f})
                        """)
        
            st.divider()  # 구분선 추가
    
        # 레이더 차트 해석 도움말
        with st.expander("📖 정규화된 레이더 차트 해석 가이드"):
            st.markdown("""
            ### 🎯 레이더 차트 읽는 방법
            
            **정규화 적용**: 모든 영양성분이 0-1 범위로 조정되어 **상대적 비교**가 가능합니다.
            
            #### 📊 차트 해석
            - **중심(0)**: 해당 영양성분이 비교 제품 중 가장 낮음
            - **외곽(1)**: 해당 영양성분이 비교 제품 중 가장 높음
            - **면적**: 전체적인 영양성분 프로필을 나타냄
            
            #### 🔍 비교 포인트
            - **단백질 중심 선택**: 단백질 축이 길고 당분 축이 짧은 제품
            - **저나트륨 선택**: 나트륨 축이 짧은 제품
            - **균형잡힌 영양**: 모든 축이 적당한 길이를 가진 제품
            - **고칼로리 회피**: 칼로리 축이 짧은 제품
            
            #### ⚠️ 주의사항
            - 이 차트는 **상대적 비교**만 보여줍니다
            - 절대적인 수치는 위의 비교표를 참고하세요
            - 높다고 항상 나쁜 것은 아닙니다 (예: 단백질, 식이섬유)
            
            #### 💡 활용 팁
            1. **목적에 맞는 선택**: 다이어트 중이라면 칼로리와 당분이 낮은 제품
            2. **운동 후 보충**: 단백질이 높은 제품
            3. **건강 관리**: 나트륨이 낮고 식이섬유가 높은 제품
            """)
    
    # 추가 분석 옵션
    st.subheader("🔍 추가 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 가격 대비 영양성분 분석"):
            st.info("가격 정보 분석 기능은 추후 업데이트 예정입니다.")
    
    with col2:
        if st.button("📈 영양성분 트렌드 분석"):
            st.info("트렌드 분석 기능은 추후 업데이트 예정입니다.")
    
    # 결과 저장
    st.subheader("💾 분석 결과 저장")
    
    if st.button("📁 분석 결과 JSON으로 저장"):
        result_data = {
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "selected_nutrients": selected_nutrients,
            "target_weights": target_weights,
            "products_analyzed": len(products_data),
            "comparison_data": comparison_df.to_dict('records') if 'comparison_df' in locals() else [],
            "products_detail": products_data
        }
        
        # 결과 폴더 생성
        if not os.path.exists('analysis_results'):
            os.makedirs('analysis_results')
        
        result_filename = f"analysis_results/nutrition_analysis_{int(datetime.now().timestamp())}.json"
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ 분석 결과가 '{result_filename}' 파일에 저장되었습니다!")
    
    # 네비게이션
    st.subheader("🧭 다음 단계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 다시 분석하기"):
            st.session_state.page = 'crawling'
            st.rerun()
    
    with col2:
        if st.button("📸 새로운 제품 분석"):
            st.session_state.page = 'img_to_analysis'
            st.rerun()
    
    with col3:
        if st.button("🏠 메인으로"):
            st.session_state.page = 'main_page'
            st.rerun()
