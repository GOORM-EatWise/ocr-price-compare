"""
Firebase 초기화 및 클라이언트 반환
# !pip install --upgrade firebase-admin  


"""
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import os
import streamlit as st
import pandas as pd
import json

FILE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# firebase 초기화
def firebase_init():
    # Firebase 앱이 이미 초기화되었는지 확인
    try:
        # 이미 초기화된 앱이 있는지 확인
        firebase_admin.get_app()
        # 이미 초기화되어 있으면 기존 클라이언트 반환
        return firestore.client()
    except ValueError:
        # 초기화되지 않은 경우에만 새로 초기화
        parents_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(parents_dir)
        cred_path = os.path.join(
            parents_dir, "db/eatwise-4dfe3-firebase-adminsdk-fbsvc-4b7495f398.json"  # firebase api key
        )
        cred = credentials.Certificate(cred_path)  # 인증 키
        firebase_admin.initialize_app(cred)
        return firestore.client()


def get_current_temp_user():
    """
    임시로 처리한 유저 정보
    페이지 연결 시 st.session_state.user_info 에 저장한 유저 정보 로드
    """
    try:
        user_dict = {
        'user_name': st.session_state.user_info['user_name'],
        "gender": st.session_state.user_info['gender'],
        "height": st.session_state.user_info['height'],
        "weight": st.session_state.user_info['weight'],
        "age": st.session_state.user_info['age'],
        }
    except:
        user_dict = {
            'user_name': "John Doe",
            "gender": "Male",
            "height": 180,
            "weight": 70,
            "age": 37,
        }
    return user_dict


def add_user_info(user_dict):
    fc = firebase_init()
    user_ref = fc.collection("user_info")
    user_ref.add(user_dict)
    df = get_user_info()
    
    return df.iloc[-1]['아이디']


def get_user_info():
    """    유저 정보 불러오기    """
    fc = firebase_init()
    columns = pd.Index(["아이디", "이름", "성별", "키", "몸무게", "나이"])
    user_df = pd.DataFrame(columns=columns)
    
    user_ref = fc.collection("user_info")
    user_list = user_ref.get()

    user_df['아이디'] = [user.id for user in user_list]
    user_list = [user.to_dict() for user in user_list]

    user_temp = pd.DataFrame(user_list)

    user_df['이름'] = user_temp['user_name']
    user_df['성별'] = user_temp['gender']
    user_df['키'] = user_temp['height']
    user_df['몸무게'] = user_temp['weight']
    user_df['나이'] = user_temp['age']

    return user_df


def delete_user(user_id: str):
    fc = firebase_init()
    user_ref = fc.collection("user_info")
    user_ref.document(user_id).delete()
    return True


def add_product_info():
    if os.path.exists(f'{FILE_PATH}/danawa_product'):
        danawa_files = [f for f in os.listdir(f'{FILE_PATH}/danawa_product') if f.startswith('similar_products') and f.endswith('.json')]
        if danawa_files:
            latest_similar = max(danawa_files, key=lambda x: os.path.getctime(f'{FILE_PATH}/danawa_product/{x}'))
            with open(f'{FILE_PATH}/danawa_product/{latest_similar}', 'r', encoding='utf-8') as f:
                similar_data = json.load(f)
                products_info = []
                product_dict = dict()
                selected_product = similar_data.get('selected_product')
                product_dict['prod_name'] = selected_product.get('prod_name')
                product_dict['price'] = selected_product.get('price')
                product_dict['volume'] = selected_product.get('volume')
                product_dict['category'] = selected_product.get('category')
                product_dict['calories'] = selected_product.get('nutrition_info').get('칼로리')
                product_dict['protein'] = selected_product.get('nutrition_info').get('단백질')
                product_dict['fat'] = selected_product.get('nutrition_info').get('지방')
                product_dict['carbohydrate'] = selected_product.get('nutrition_info').get('탄수화물')
                product_dict['sodium'] = selected_product.get('nutrition_info').get('나트륨')
                product_dict['sugar'] = selected_product.get('nutrition_info').get('당분')
                products_info.append(product_dict)

                similar_products = similar_data.get('similar_products', [])
                for similar_product in similar_products:
                    product_dict = dict()
                    product_dict['prod_name'] = similar_product.get('prod_name')
                    product_dict['price'] = similar_product.get('price')
                    product_dict['volume'] = similar_product.get('volume')
                    product_dict['category'] = similar_product.get('category')
                    product_dict['calories'] = similar_product.get('nutrition').get('칼로리')
                    product_dict['protein'] = similar_product.get('nutrition').get('단백질')
                    product_dict['fat'] = similar_product.get('nutrition').get('지방')
                    product_dict['carbohydrate'] = similar_product.get('nutrition').get('탄수화물')
                    product_dict['sodium'] = similar_product.get('nutrition').get('나트륨')
                    product_dict['sugar'] = similar_product.get('nutrition').get('당분')
                    products_info.append(product_dict)

                st.dataframe(products_info)

                fc = st.session_state.firebase_client = firebase_init()
                product_ref = fc.collection("products_info")
                for product in products_info:
                    product_ref.add(product)

                return True
        else:
                return False
    else:
        return False
    

def get_product_info():
    fc = firebase_init()
    delete_duplicated_product()
    product_ref = fc.collection("products_info")
    product_list = product_ref.get()
    product_df = pd.DataFrame([product.to_dict() for product in product_list])

    # 컬럼 순서를 원하는 순서로 재정렬
    if not product_df.empty:
        # 원하는 컬럼 순서 정의
        column_order = ['prod_name', 'price', 'volume', 'calories', 'protein', 'fat', 'carbohydrate', 'sodium', 'sugar', 'category']
        
        # 존재하는 컬럼만 필터링하여 순서 재정렬
        existing_columns = [col for col in column_order if col in product_df.columns]
        product_df = product_df[existing_columns]
    
    return product_df


def delete_duplicated_product():
    fc = firebase_init()
    product_ref = fc.collection("products_info")
    product_list = product_ref.get()
    seen_products = set()
    products_to_delete = []
    
    for product in product_list:
        product_data = product.to_dict()
        if product_data is None:
            continue
        # 상품명과 용량을 기준으로 중복 판단
        product_key = f"{product_data.get('prod_name', '')}_{product_data.get('volume', '')}"
        
        if product_key in seen_products:
            products_to_delete.append(product.id)
        else:
            seen_products.add(product_key)
    
    # 중복된 상품들 삭제
    for product_id in products_to_delete:
        product_ref.document(product_id).delete()
    
    # 삭제 후 남은 상품들을 DataFrame으로 변환
    remaining_products = product_ref.get()
    product_df = pd.DataFrame([product.to_dict() for product in remaining_products])
    
    # 컬럼 순서를 원하는 순서로 재정렬
    if not product_df.empty:
        # 원하는 컬럼 순서 정의
        column_order = ['prod_name', 'price', 'volume', 'calories', 'protein', 'fat', 'carbohydrate', 'sodium', 'sugar', 'category']
        
        # 존재하는 컬럼만 필터링하여 순서 재정렬
        existing_columns = [col for col in column_order if col in product_df.columns]
        product_df = product_df[existing_columns]
    return product_df


def add_favorite_product(favorite_prod_idx):
    fc = firebase_init()
    product_df = get_product_info()
    favorite_product = product_df.iloc[favorite_prod_idx]
    # favorite_product['user_id'] = st.session_state.user_info['user_id']
    favorite_product['user_id'] = "gf8LZeek4EYDUtdnqC6A" # 임시로 강제 지정

    favorite_product_ref = fc.collection("favorite_products")
    favorite_product_ref.add(favorite_product.to_dict())
    
    return True 

    
def get_favorite_product():
    fc = firebase_init()
    favorite_product_ref = fc.collection("favorite_products")
    product_list = favorite_product_ref.get()
    product_df = pd.DataFrame([product.to_dict() for product in product_list])

    # 컬럼 순서를 원하는 순서로 재정렬
    if not product_df.empty:
        # 원하는 컬럼 순서 정의
        column_order = ['prod_name', 'price', 'volume', 'calories', 'protein', 'fat', 'carbohydrate', 'sodium', 'sugar', 'category', 'user_id']
        
        # 존재하는 컬럼만 필터링하여 순서 재정렬
        existing_columns = [col for col in column_order if col in product_df.columns]
        product_df = product_df[existing_columns]

        current_user_id = product_df['user_id'].iloc[0] # type: ignore

    
    return current_user_id, product_df

def delete_favorite_product(prod_name):
    fc = firebase_init()
    user_id = None
    try: 
        user_id = st.session_state.user_info['user_id']
    except:
        user_id = get_user_info().iloc[-1]['아이디'] # 임시로 강제 지정
        
    favorite_product_ref = fc.collection("favorite_products")
    product_list = favorite_product_ref.where('user_id', '==', user_id).get()
    for product in product_list:
        if product.to_dict()['prod_name'] == prod_name:                      # type: ignore
            favorite_product_ref.document(product.id).delete()
            break
    return True


def render():
    st.title("🍎 DB 관리")

    # 파이어베이스 클라이언트 초기화
    fc = firebase_init()
    user_ref = fc.collection("user_info") # 유저 정보 컬렉션 참조

    # 삭제 폼 및 유저 정보 추가 폼  
    st.markdown("### 고객 정보")

    with st.form(key="user_info_form", clear_on_submit=True):
        st.dataframe(get_user_info())
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(pd.DataFrame([get_current_temp_user()]))
            submit_add = st.form_submit_button("현재 고객 추가")
            if submit_add:
                user_dict = get_current_temp_user()
                user_id = add_user_info(user_dict)
                st.success(f"아이디 '{user_id}'의 고객 정보가 추가되었습니다.")
                # 페이지를 다시 로드하여 데이터 갱신
                st.rerun()

        with col2:
            user_id = st.text_input("삭제할 고객의 아이디를 입력해주세요")
            submit_delete = st.form_submit_button("고객 정보 삭제")

            if submit_delete and user_id:
                    delete_user(user_id)
                    st.success(f"아이디 '{user_id}'의 고객 정보가 삭제되었습니다.")
                    # 페이지를 다시 로드하여 데이터 갱신
                    st.rerun()

    st.divider()

    with st.form(key="product_info_form", clear_on_submit=True):
        st.dataframe(get_product_info())

        col1, col2 = st.columns(2)

        with col1:
            submit_add = st.form_submit_button("상품 정보 추가", icon="🥙")
            if submit_add:
                add_product_info()
                st.success("상품 정보가 추가되었습니다.")
                # 페이지를 다시 로드하여 데이터 갱신
                st.rerun()
        with col2:
            favorite_product_num = st.number_input("즐겨찾기 상품 번호를 입력해주세요", min_value=0, max_value=10, value=1)
            submit_add = st.form_submit_button("즐겨찾기 상품 추가")
            if submit_add:
                add_favorite_product(int(favorite_product_num))
                st.success("즐겨찾기 상품이 추가되었습니다.")
                # 페이지를 다시 로드하여 데이터 갱신
                st.rerun()

    st.divider()  

    with st.form(key="favorite_product_form", clear_on_submit=True):
        favorite_product_name = st.text_input("삭제할 즐겨찾기 상품 이름을 입력해주세요")
        submit_delete = st.form_submit_button("즐겨찾기 상품 삭제")
        if submit_delete and favorite_product_name:
            delete_favorite_product(favorite_product_name)
            st.success("즐겨찾기 상품이 삭제되었습니다.")
            # 페이지를 다시 로드하여 데이터 갱신
            st.rerun()

        current_user_id, favorite_product_df = get_favorite_product()
        st.write(f"{current_user_id} 님의 즐겨찾기 상품")
        st.dataframe(favorite_product_df)



if __name__ == "__main__":
    render()