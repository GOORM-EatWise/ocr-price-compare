from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import re
import gc


class PriceCleaningPipeline:
    """Clean and normalize price information"""
    
    def __init__(self):
        # Regex to keep only digits and commas in price
        self.price_pattern = re.compile(r'[^\d]')
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        price_text = adapter.get('price')
        
        if price_text:
            cleaned_price = self.price_pattern.sub('', price_text).strip()
            if cleaned_price:
                adapter['price'] = cleaned_price
        
        return item


class NutrientExtractionPipeline:
    """Converts aggregated nutrition info into separate fields"""
    def __init__(self):
        self.nutrient_patterns = {
            'per_serving': re.compile(r'(?:1회\s*제공량|제공량|표시기준분량|표시기준량)[:\s]*([0-9,]+(?:\.[0-9]+)?)\s*(g|ml)'),
            'kcal': re.compile(r'열량[:\s]*([0-9,]+(?:\.[0-9]+)?)\s*kcal'),
            'carb': re.compile(r'탄수화물[:\s]*([0-9,]+(?:\.[0-9]+)?)'),
            'sugar': re.compile(r'당류[:\s]*([0-9,]+(?:\.[0-9]+)?)'),
            'protein': re.compile(r'단백질[:\s]*([0-9,]+(?:\.[0-9]+)?)'),
            'fat': re.compile(r'지방[:\s]*([0-9,]+(?:\.[0-9]+)?)'),
        }
    

    def extract_nutrient_value(self, spec_origin, field_name):
        """Returns clean numeric value without commas"""
        if not spec_origin or field_name not in self.nutrient_patterns:
            return ""
        
        match = self.nutrient_patterns[field_name].search(spec_origin)
        
        if match:
            value = match.group(1) + (match.group(2) if field_name == 'per_serving' else '')
            return value
        
        return ""
    
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spec_origin = adapter.get('spec_origin', '')
        
        adapter['per_serving'] = self.extract_nutrient_value(spec_origin, 'per_serving')
        adapter['kcal'] = self.extract_nutrient_value(spec_origin, 'kcal')
        adapter['carb'] = self.extract_nutrient_value(spec_origin, 'carb')
        adapter['sugar'] = self.extract_nutrient_value(spec_origin, 'sugar')
        adapter['protein'] = self.extract_nutrient_value(spec_origin, 'protein')
        adapter['fat'] = self.extract_nutrient_value(spec_origin, 'fat')
        
        return item


class DuplicatesPipeline:
    """Memory-efficient hash-based duplicate removal using SHA224"""

    def __init__(self):
        self.seen_names = set()


    def process_item(self, item, spider):
        """Process item and check for duplicates"""
        adapter = ItemAdapter(item)
        product_name = adapter.get('prod_name', '').strip()
        
        if not product_name:
            raise DropItem("Empty product name")
        
        if product_name in self.seen_names:
            raise DropItem(f"Duplicate product detected")
        
        self.seen_names.add(product_name)
        
        return item
    

    def close_spider(self, spider):
        """Clean up memory when spider closes"""
        self.seen_names.clear()
        gc.collect()  