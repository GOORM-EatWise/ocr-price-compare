import scrapy
from danawa_crawler.items import NutritionProductItem
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import gc


class ProductSpider(scrapy.Spider):
    name = "product" # spider name

    def __init__(self, search_keyword="", pages=1, **kwargs):
        super().__init__(**kwargs)
        
        # Set search parameters with defaults
        self.search_keyword = search_keyword
        self.max_pages = int(pages)
        self.item_count = 0
        
        self.parser = "lxml"  # Fast HTML parser
        
        self.text_clean_pattern = re.compile(r'\s+') 
        self.required_nutrients = ['단백질']
        # self.required_nutrients = ['탄수화물', '당류', '단백질', '지방']


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Override from_crawler to store search_keyword for settings update"""
        spider = super().from_crawler(crawler, *args, **kwargs)
        if "search_keyword" in kwargs:
            
            feeds = spider.settings.get('FEEDS', {})

            search_keyword = kwargs.get('search_keyword', '')

            filename = f"{search_keyword}_nutrition_data.json"
            
            # Add new feed configuration
            feeds[filename] = {
                'format': 'json',              # Export format
                'encoding': 'utf8',            # File encoding
                'ensure_ascii': False,         # Allow non-ASCII characters (Korean)
                'indent': 2,                   # Pretty print with 2-space indentation
                'overwrite': True,             # Overwrite existing file
            }
            
            spider.settings.set('FEEDS', feeds) 
            
        return spider


    def clean_html(self, raw_html):
        """Removes HTML tags and normalizes whitespace"""
        if not raw_html:
            return ""
        
        try:
            soup = BeautifulSoup(raw_html, self.parser)
            text = soup.get_text(separator=" ", strip=True)

            return self.text_clean_pattern.sub(' ', text).strip()

        except Exception:
            return ""


    def has_required_nutrients_info(self, spec_text):
        """Check Required nutrients: carbohydrate, sugar, protein, fat"""
        if not spec_text:
            return False
        
        return all(nutrient in spec_text for nutrient in self.required_nutrients)
        

    async def start(self):
        """Generate URLs for crawling and send requests"""
        query_encoded = quote(self.search_keyword.replace(' ', '+'))
        
        for page in range(1, self.max_pages + 1):
            url = (f"https://search.danawa.com/dsearch.php?"
                   f"query={query_encoded}&"
                   f"originalQuery={query_encoded}&"
                   f"checkedInfo=N&"
                   f"volumeType=allvs&"
                   f"page={page}")
            
            yield scrapy.Request(
                url=url, 
                callback=self.parse,
                errback=self.handle_error,
                dont_filter=True
            )

        
    def parse(self, response):
            """Extract product information from page"""
            product_list = response.css('li.prod_item')
            
            if not product_list:
                return
            
            processed_count = 0
            
            for product in product_list:
                try:
                    spec_html = product.css(".prod_item div.spec_list").get()

                    if not self.has_required_nutrients_info(spec_html):
                        continue

                    prod_name_html = product.css("a.click_log_product_standard_title_").get()
                    price_html = product.css("a.click_log_product_standard_price_").get()
                    
                    if prod_name_html and price_html:
                        self.item_count += 1
                        processed_count += 1
                        
                        # Create Item with cleaned text data
                        item = NutritionProductItem()
                        item['item_num'] = self.item_count
                        item['prod_name'] = self.clean_html(prod_name_html)
                        item['spec_origin'] = self.clean_html(spec_html)
                        item['price'] = self.clean_html(price_html)
                        
                        yield item
                    
                except Exception as e:
                    self.logger.error(f"Product parsing error: {e}")
                    continue
        
            if processed_count > 0:
                gc.collect()


    def handle_error(self, failure):
        """Handle request failures with detailed logging"""
        self.logger.error(f"Request failed: {failure.value}")

    def closed(self, reason):
        """Final cleanup and logging"""
        gc.collect()
        
        # Minimal completion log
        if hasattr(self, 'logger') and self.item_count > 0:
            self.logger.warning(f"Collected {self.item_count} items")