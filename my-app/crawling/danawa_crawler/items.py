import scrapy

class NutritionProductItem(scrapy.Item):
    """영양정보가 포함된 상품 아이템"""
    
    item_num = scrapy.Field()                            # 상품 번호
    prod_name = scrapy.Field()                            # 상품명
    price = scrapy.Field()                                # 가격

    spec_origin = scrapy.Field()                          # 영양정보 원본
    per_serving = scrapy.Field()                          # 1회 제공량
    kcal = scrapy.Field()                                 # 칼로리
    carb = scrapy.Field()                                 # 탄수화물
    protein = scrapy.Field()                              # 단백질
    sugar = scrapy.Field()                                # 당
    fat = scrapy.Field()                                  # 지방