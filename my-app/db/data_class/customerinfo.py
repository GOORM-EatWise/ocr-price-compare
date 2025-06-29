class CustomerInfo:
    """고객 정보를 입력할 CustomerInfo 클래스 정의"""

    def __init__(self, user_info: dict):
        self.user_name = user_info["user_name"]
        self.user_sex = user_info["user_sex"]
        self.user_height = user_info["user_height"]
        self.user_weight = user_info["user_weight"]
        self.user_age = user_info["user_age"]

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "user_sex": self.user_sex,
            "user_height": self.user_height,
            "user_weight": self.user_weight,
            "user_age": self.user_age,
        }

    def __repr__(self):  # 디버깅 시 보낼 데이터
        return f"CustomerInfo(user_name={self.user_name}, user_sex={self.user_sex}, user_height={self.user_height}, user_weight={self.user_weight}, user_age={self.user_age})"
