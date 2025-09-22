#!/usr/bin/env python3
"""
LeBonCoin Graphics Card Scraper
Scrapes the 100 latest posted graphic cards from LeBonCoin
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any
from seleniumbase import SB
import requests
from urllib.parse import urljoin

class LeBonCoinScraper:
    def __init__(self):
        self.base_url = "https://www.leboncoin.fr"
        self.search_url = "https://www.leboncoin.fr/recherche?category=15&text=carte%20graphique&sort=time&order=desc"
        
    def scrape_graphics_cards(self, max_products: int = 100) -> List[Dict[str, Any]]:
        """Scrape graphics cards from LeBonCoin"""
        products = []
        
        print(f"🔍 Starting LeBonCoin scraper for graphics cards...")
        print(f"🎯 Target: {max_products} products")
        
        with SB(uc=True, headless=True) as sb:
            try:
                # Navigate to search page
                print(f"📍 Navigating to: {self.search_url}")
                sb.uc_open_with_reconnect(self.search_url, reconnect_time=5)
                sb.sleep(3)
                
                # Wait for content to load
                sb.wait_for_element("div[data-testid='adCard']", timeout=10)
                
                page = 1
                while len(products) < max_products:
                    print(f"📄 Scraping page {page}...")
                    
                    # Get product cards on current page
                    cards = sb.find_elements("div[data-testid='adCard']")
                    if not cards:
                        print("❌ No product cards found, stopping")
                        break
                    
                    page_products = 0
                    for card in cards:
                        if len(products) >= max_products:
                            break
                            
                        try:
                            # Extract product information
                            product_data = self._extract_product_data(card)
                            if product_data:
                                products.append(product_data)
                                page_products += 1
                                print(f"  ✅ {len(products)}. {product_data['name'][:50]}... - {product_data['price']}")
                            
                        except Exception as e:
                            print(f"  ❌ Error extracting product: {str(e)}")
                            continue
                    
                    print(f"📊 Page {page}: {page_products} products collected (Total: {len(products)})")
                    
                    if len(products) >= max_products:
                        break
                    
                    # Try to go to next page
                    try:
                        next_button = sb.find_element("a[data-testid='pagination-next']")
                        if next_button and next_button.is_enabled():
                            print("➡️ Going to next page...")
                            sb.click(next_button)
                            sb.sleep(3)
                            page += 1
                        else:
                            print("❌ No next page available")
                            break
                    except Exception as e:
                        print(f"❌ Error navigating to next page: {str(e)}")
                        break
                
            except Exception as e:
                print(f"❌ Error during scraping: {str(e)}")
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total products collected: {len(products)}")
        
        return products
    
    def _extract_product_data(self, card) -> Dict[str, Any]:
        """Extract product data from a card element"""
        try:
            # Product name
            name_element = card.find_element("p[data-testid='adCardTitle']")
            name = name_element.text.strip()
            
            # Price
            price_element = card.find_element("span[data-testid='adCardPrice']")
            price = price_element.text.strip()
            
            # Location
            location_element = card.find_element("p[data-testid='adCardLocation']")
            location = location_element.text.strip()
            
            # Date
            date_element = card.find_element("p[data-testid='adCardDate']")
            date = date_element.text.strip()
            
            # URL
            link_element = card.find_element("a")
            url = urljoin(self.base_url, link_element.get_attribute("href"))
            
            # Create product data
            product_data = {
                "name": name,
                "price": price,
                "location": location,
                "date": date,
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "leboncoin"
            }
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error extracting product data: {str(e)}")
            return None
    
    def save_to_file(self, products: List[Dict[str, Any]], filename: str = None):
        """Save products to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leboncoin_graphics_cards_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {filename}")
        return filename

def main():
    """Main function to run the scraper"""
    scraper = LeBonCoinScraper()
    
    # Scrape graphics cards
    products = scraper.scrape_graphics_cards(max_products=100)
    
    # Save to file
    if products:
        scraper.save_to_file(products)
    else:
        print("❌ No products found to save")

if __name__ == "__main__":
    main()