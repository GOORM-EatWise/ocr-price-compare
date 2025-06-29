import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore  # Firestore를 사용하기 위해 임포트합니다
import os


def firebase_init():
    # Firebase 앱이 이미 초기화되었는지 확인
    try:
        # 이미 초기화된 앱이 있는지 확인
        firebase_admin.get_app()
        # 이미 초기화되어 있으면 기존 클라이언트 반환
        return firestore.client()
    except ValueError:
        # 초기화되지 않은 경우에만 새로 초기화
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(
            current_dir, "eatwise-4dfe3-firebase-adminsdk-fbsvc-4b7495f398.json"
        )
        cred = credentials.Certificate(cred_path)  # 인증 키
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db


def login_init():
    """임시로 간단하게 로그인 프로세스 구현"""

    if "db" not in st.session_state:
        st.session_state["db"] = firebase_init()

    return True


def home():
    # 페이지 설정
    st.set_page_config(
        page_title="Home",
        page_icon="🍎",
        layout="wide",
    )


if "login_status" not in st.session_state:
    st.session_state["login_status"] = login_init()


pg = st.navigation(
    [
        st.Page(home, title="home", icon="🏠"),
        st.Page("customer_page.py", title="customers", icon="🔠"),
        st.Page("product_page.py", title="product", icon="🥙"),
    ]
)

pg.run()


# on_click, on_change로 이용해 로그인 구현 가능
