import streamlit as st
from data_class.customerinfo import CustomerInfo
import pandas as pd


def add_customer_data(user_id: str, customerinfo: CustomerInfo):
    db = st.session_state["db"]
    customerinfo_ref = db.collection("customer_info")
    try:
        customerinfo_ref.document(user_id).set(customerinfo.to_dict())
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {str(e)}")
        return False


def get_customer_data_all():
    db = st.session_state["db"]
    customerinfo_ref = db.collection("customer_info")
    docs = customerinfo_ref.get()

    # 문서 ID와 데이터를 함께 가져오기
    data_list = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["user_id"] = doc.id  # 문서 ID를 user_id 필드에 추가
        data_list.append(doc_data)

    df = pd.DataFrame(data_list)
    return df


def print_customer_status():
    db_data = get_customer_data_all()

    # pd.Index를 사용해서 columns 지정
    columns = pd.Index(
        ["user_id", "user_name", "user_height", "user_weight", "user_age", "user_sex"]
    )
    data_df = pd.DataFrame(columns=columns)

    # 데이터가 있으면 DataFrame에 추가
    if not db_data.empty:
        data_df = pd.concat([data_df, db_data], ignore_index=True)

    st.write("## 임시 회원 데이터 확인")
    st.dataframe(data_df)

    return True


def delete_customer_data(user_id: str):
    db = st.session_state["db"]
    customerinfo_ref = db.collection("customer_info")
    customerinfo_ref.document(user_id).delete()
    return True


# 페이지 설정
st.set_page_config(
    page_title="Customer Info",
    page_icon="👤",
)

st.title("고객 정보 입력")

with st.form(key="customer_add_form", clear_on_submit=True):
    user_info = {
        "user_name": "",
        "user_sex": "",
        "user_height": 0,
        "user_weight": 0,
        "user_age": 0,
    }
    user_id = ""

    col1, col2 = st.columns(2)
    with col1:
        st.write("아이디")
        user_id = st.text_input("아이디를 입력해주세요")
    with col2:
        st.write("이름")
        user_info["user_name"] = st.text_input("이름을 입력해주세요")
    col1, col2 = st.columns(2)
    with col1:
        st.write("키")
        user_info["user_height"] = st.number_input("키를 입력해주세요", value=None)
    with col2:
        st.write("몸무게")
        user_info["user_weight"] = st.number_input("몸무게를 입력해주세요", value=None)

    col1, col2 = st.columns(2)
    with col1:
        st.write("나이")
        user_info["user_age"] = st.number_input("나이를 입력해주세요", value=None)

    with col2:
        st.write("성별")
        user_info["user_sex"] = st.selectbox(
            label="성별을 선택해주세요", options=["남자", "여자"], index=0
        )

    submit = st.form_submit_button("고객 정보 추가")

    if submit:
        customerinfo = CustomerInfo(user_info)
        add_customer_data(user_id, customerinfo)

    print_customer_status()

# 구분선 추가
st.divider()

# 삭제 폼
st.subheader("고객 정보 삭제")
with st.form(key="customer_delete_form", clear_on_submit=True):
    user_id = st.text_input("삭제할 고객의 아이디를 입력해주세요")
    submit = st.form_submit_button("고객 정보 삭제")

    if submit:
        delete_customer_data(user_id)
        st.success(f"아이디 '{user_id}'의 고객 정보가 삭제되었습니다.")
        # 페이지를 다시 로드하여 데이터 갱신
        st.rerun()
