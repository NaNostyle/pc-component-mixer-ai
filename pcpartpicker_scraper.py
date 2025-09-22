#!/usr/bin/env python3
"""
PC Part Picker Scraper using SeleniumBase
Author: AI Assistant
Description: Advanced web scraper for pcpartpicker.com using SeleniumBase framework
"""

import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from seleniumbase import BaseCase


@dataclass
class ComponentData:
    """Data structure for PC components"""
    name: str
    price: str
    vendor: str
    availability: str
    rating: str = ""
    specifications: Dict[str, str] = None
    url: str = ""
    category: str = ""
    scraped_at: str = ""
    
    def __post_init__(self):
        if self.specifications is None:
            self.specifications = {}
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


class PCPartPickerScraper(BaseCase):
    """
    Advanced PC Part Picker scraper using SeleniumBase
    
    Features:
    - Stealth mode for avoiding detection
    - Robust error handling
    - Data export to CSV/JSON
    - Multiple component categories
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://pcpartpicker.com"
        self.scraped_data: List[ComponentData] = []
        
        # Component categories and their URLs
        self.categories = {
            "cpu": "/products/cpu/",
            "motherboard": "/products/motherboard/",
            "memory": "/products/memory/",
            "storage": "/products/internal-hard-drive/",
            "video-card": "/products/video-card/",
            "case": "/products/case/",
            "power-supply": "/products/power-supply/",
            "cpu-cooler": "/products/cpu-cooler/",
            "optical-drive": "/products/optical-drive/",
            "sound-card": "/products/sound-card/",
            "wired-network-card": "/products/wired-network-card/",
            "wireless-network-card": "/products/wireless-network-card/"
        }

    def setup_browser(self, stealth_mode: bool = True):
        """Configure browser for optimal scraping"""
        if stealth_mode:
            # Use undetected Chrome mode
            self.uc_open_with_reconnect("about:blank", reconnect_time=2)
        
        # Set user agent and other headers to appear more human-like
        self.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    def scrape_component_category(self, category: str, max_pages: int = 5) -> List[ComponentData]:
        """
        Scrape components from a specific category
        
        Args:
            category: Component category (cpu, motherboard, etc.)
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of ComponentData objects
        """
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Available: {list(self.categories.keys())}")
        
        category_data = []
        category_url = self.base_url + self.categories[category]
        
        print(f"🔍 Scraping {category} from {category_url}")
        
        try:
            # Navigate to category page
            self.open(category_url)
            self.wait_for_element_present("table.xs-col-12", timeout=10)
            
            for page in range(1, max_pages + 1):
                print(f"📄 Scraping page {page} of {category}")
                
                # Extract component data from current page
                components = self._extract_components_from_page(category)
                category_data.extend(components)
                
                # Check if next page exists and navigate
                if not self._go_to_next_page():
                    print(f"✅ Reached last page for {category}")
                    break
                    
                # Be respectful with delays
                self.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping {category}: {str(e)}")
            
        return category_data

    def _extract_components_from_page(self, category: str) -> List[ComponentData]:
        """Extract component data from current page"""
        components = []
        
        try:
            # Wait for the product table to load
            self.wait_for_element_present("table.xs-col-12 tbody tr", timeout=10)
            
            # Get all product rows
            rows = self.find_elements("table.xs-col-12 tbody tr")
            
            for row in rows:
                try:
                    component_data = self._parse_component_row(row, category)
                    if component_data:
                        components.append(component_data)
                except Exception as e:
                    print(f"⚠️ Error parsing row: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error extracting components: {str(e)}")
            
        return components

    def _parse_component_row(self, row, category: str) -> Optional[ComponentData]:
        """Parse individual component row"""
        try:
            # Component name (usually in first or second column)
            name_element = row.find_element("css selector", "td.xs-col-12 a")
            name = name_element.text.strip() if name_element else "Unknown"
            product_url = name_element.get_attribute("href") if name_element else ""
            
            # Price (look for price cell)
            price_elements = row.find_elements("css selector", "td[data-sort-value], .td__price")
            price = "N/A"
            for elem in price_elements:
                text = elem.text.strip()
                if "$" in text:
                    price = text
                    break
            
            # Vendor/Store (usually in a specific column)
            vendor_elements = row.find_elements("css selector", "td a[href*='outbound'], .td__vendor")
            vendor = "Unknown"
            if vendor_elements:
                vendor = vendor_elements[0].text.strip()
            
            # Availability (check for stock status)
            availability = "Unknown"
            stock_elements = row.find_elements("css selector", ".td__availability, [class*='stock']")
            if stock_elements:
                availability = stock_elements[0].text.strip()
            
            # Rating (if available)
            rating = ""
            rating_elements = row.find_elements("css selector", "[class*='rating'], .td__rating")
            if rating_elements:
                rating = rating_elements[0].text.strip()
            
            return ComponentData(
                name=name,
                price=price,
                vendor=vendor,
                availability=availability,
                rating=rating,
                url=product_url,
                category=category
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing component row: {str(e)}")
            return None

    def _go_to_next_page(self) -> bool:
        """Navigate to next page if available"""
        try:
            # Look for next page button
            next_buttons = self.find_elements("[class*='next'], a[href*='page=']")
            
            for button in next_buttons:
                if "next" in button.get_attribute("class").lower() or "›" in button.text:
                    if not button.get_attribute("disabled"):
                        self.click(button)
                        self.wait_for_element_present("table.xs-col-12 tbody tr", timeout=10)
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error navigating to next page: {str(e)}")
            return False

    def scrape_all_categories(self, max_pages_per_category: int = 3) -> Dict[str, List[ComponentData]]:
        """
        Scrape all component categories
        
        Args:
            max_pages_per_category: Maximum pages to scrape per category
            
        Returns:
            Dictionary with category names as keys and component lists as values
        """
        all_data = {}
        
        print(f"🚀 Starting full scrape of PC Part Picker")
        print(f"📊 Categories to scrape: {list(self.categories.keys())}")
        
        for category in self.categories.keys():
            print(f"\n🔧 Scraping {category.upper()} components...")
            category_data = self.scrape_component_category(category, max_pages_per_category)
            all_data[category] = category_data
            self.scraped_data.extend(category_data)
            
            print(f"✅ {category}: {len(category_data)} components scraped")
            
            # Be respectful with delays between categories
            self.sleep(3)
        
        print(f"\n🎉 Scraping complete! Total components: {len(self.scraped_data)}")
        return all_data

    def save_to_csv(self, filename: str = None) -> str:
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pcpartpicker_data_{timestamp}.csv"
        
        if not self.scraped_data:
            print("⚠️ No data to save")
            return filename
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'price', 'vendor', 'availability', 'rating', 'url', 'category', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for component in self.scraped_data:
                writer.writerow(asdict(component))
        
        print(f"💾 Data saved to {filename}")
        return filename

    def save_to_json(self, filename: str = None) -> str:
        """Save scraped data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pcpartpicker_data_{timestamp}.json"
        
        if not self.scraped_data:
            print("⚠️ No data to save")
            return filename
        
        data_dict = [asdict(component) for component in self.scraped_data]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data_dict, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to {filename}")
        return filename

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of scraped data"""
        if not self.scraped_data:
            return {"total_components": 0}
        
        stats = {
            "total_components": len(self.scraped_data),
            "categories": {},
            "price_ranges": {},
            "vendors": {}
        }
        
        # Category breakdown
        for component in self.scraped_data:
            category = component.category
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # Vendor breakdown
            vendor = component.vendor
            stats["vendors"][vendor] = stats["vendors"].get(vendor, 0) + 1
        
        return stats


# Example usage
if __name__ == "__main__":
    def run_scraper_demo():
        """Demo function showing how to use the scraper"""
        scraper = PCPartPickerScraper()
        
        try:
            # Setup browser with stealth mode
            scraper.setup_browser(stealth_mode=True)
            
            # Option 1: Scrape specific category
            print("🔍 Scraping CPU components...")
            cpu_data = scraper.scrape_component_category("cpu", max_pages=2)
            
            # Option 2: Scrape all categories (commented out for demo)
            # all_data = scraper.scrape_all_categories(max_pages_per_category=1)
            
            # Save data
            scraper.save_to_csv()
            scraper.save_to_json()
            
            # Show summary
            stats = scraper.get_summary_stats()
            print(f"\n📊 Summary: {json.dumps(stats, indent=2)}")
            
        except Exception as e:
            print(f"❌ Error in demo: {str(e)}")
        finally:
            if hasattr(scraper, 'driver') and scraper.driver:
                scraper.driver.quit()
    
    # Uncomment to run demo
    # run_scraper_demo()