import scrapy
from danawa_crawler.items import NutritionProductItem
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import gc


class DanawaSpider(scrapy.Spider):
    name = "danawa" # spider name

    def __init__(self, search_keyword="그릭 요거트", pages=4, **kwargs):
        super().__init__(**kwargs)
        
        # Set search parameters with defaults
        self.search_keyword = search_keyword
        self.max_pages = int(pages)
        self.item_count = 0
        
        self.parser = "lxml"  # Fast HTML parser
        
        self.text_clean_pattern = re.compile(r'\s+') 
        self.required_nutrients = ['탄수화물', '당류', '단백질', '지방']


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Override from_crawler to store search_keyword for settings update"""
        spider = super().from_crawler(crawler, *args, **kwargs)
        if "search_keyword" in kwargs:
            
            feeds = spider.settings.get('FEEDS', {})

            search_keyword = kwargs.get('search_keyword', '그릭 요거트')

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


    # @classmethod
    # def update_settings(cls, settings):
    #     """Update spider settings to include dynamic filename based on search keyword"""
    #     super().update_settings(settings)
        
    #     # Get the search keyword from spider arguments or use default
    #     search_keyword = DanawaSpider._search_keyword
        
    #     # Clean the keyword for use in filename (remove special characters)
    #     clean_keyword = re.sub(r'[^\w\s-]', '', search_keyword).strip()
    #     clean_keyword = re.sub(r'[-\s]+', '_', clean_keyword)
        
    #     # Update FEEDS setting with dynamic filename
    #     feeds = settings.get('FEEDS', {})
        
    #     # Create filename with timestamp and search keyword
    #     filename = f"{clean_keyword}_nutrition_data.json"
        
    #     # Add new feed configuration
    #     feeds[filename] = {
    #         'format': 'json',
    #         'encoding': 'utf8',
    #         'store_empty': False,
    #         'indent': 2
    #     }
        
    #     settings.set('FEEDS', feeds)   


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