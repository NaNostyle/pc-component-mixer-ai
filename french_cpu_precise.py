#!/usr/bin/env python3
"""
Precise French PC Part Picker CPU Scraper
Targets exact product table rows to get exactly 100 products per page
"""

from seleniumbase import SB
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import re
import os

def scrape_french_cpus_precise():
    """Scrape CPUs with precise targeting of product rows"""
    
    with SB(uc=True, test=True, locale="fr") as sb:
        print("🚀 Starting Precise French PC Part Picker CPU scraper...")
        
        # Start URL - French PC Part Picker sorted by price (lowest first)
        start_url = "https://fr.pcpartpicker.com/products/cpu/#sort=price&page=1"
        
        # Use UC Mode to open with Cloudflare bypass
        print("🔓 Opening French PC Part Picker with Cloudflare bypass...")
        sb.uc_open_with_reconnect(start_url, reconnect_time=3)
        
        # Handle any CAPTCHA that might appear
        print("🤖 Checking for CAPTCHA...")
        try:
            sb.uc_gui_click_captcha()
            print("✅ CAPTCHA handled successfully")
        except:
            print("ℹ️ No CAPTCHA detected")
        
        # Wait for page to load
        sb.sleep(3)
        
        # Get page title to verify we're on the right page
        title = sb.get_title()
        print(f"📄 Page title: {title}")
        
        # Initialize data storage
        all_cpus = []
        page_num = 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"french_cpus_precise_{timestamp}.json"
        csv_file = f"french_cpus_precise_{timestamp}.csv"
        
        print(f"💾 Will save to: {json_file}")
        
        while page_num <= 10:  # Limit to 10 pages (1000 products max)
            print(f"\n📄 Processing page {page_num}...")
            
            try:
                # Wait for the product table to load
                sb.wait_for_element("table#product-table", timeout=10)
                
                # Get all product rows - these are the actual product entries
                product_rows = sb.find_elements("table#product-table tbody tr")
                
                if not product_rows:
                    print("❌ No product rows found on this page")
                    break
                
                print(f"🔍 Found {len(product_rows)} product rows")
                
                page_cpus = []
                for i, row in enumerate(product_rows):
                    try:
                        # Extract data from each row
                        cells = row.find_elements("td")
                        if len(cells) < 4:  # Skip incomplete rows
                            continue
                        
                        # Product name (usually in first cell with link)
                        name_cell = cells[0]
                        name_link = name_cell.find_element("a")
                        product_name = name_link.text.strip()
                        product_url = name_link.get_attribute("href")
                        
                        # Price (usually in second cell)
                        price_cell = cells[1]
                        price_text = price_cell.text.strip()
                        
                        # Rating (usually in third cell)
                        rating_cell = cells[2]
                        rating_text = rating_cell.text.strip()
                        
                        # Compatibility (usually in fourth cell)
                        compat_cell = cells[3]
                        compat_text = compat_cell.text.strip()
                        
                        # Create product data
                        cpu_data = {
                            "name": product_name,
                            "price": price_text,
                            "rating": rating_text,
                            "compatibility": compat_text,
                            "url": product_url,
                            "page": page_num,
                            "row_index": i + 1,
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        page_cpus.append(cpu_data)
                        print(f"  ✅ {i+1}. {product_name[:50]}... - {price_text}")
                        
                    except Exception as e:
                        print(f"  ❌ Error processing row {i+1}: {str(e)}")
                        continue
                
                if not page_cpus:
                    print("❌ No valid CPUs found on this page")
                    break
                
                all_cpus.extend(page_cpus)
                print(f"📊 Page {page_num}: {len(page_cpus)} CPUs collected (Total: {len(all_cpus)})")
                
                # Check if we have enough products
                if len(all_cpus) >= 1000:
                    print("🎯 Reached target of 1000 products")
                    break
                
                # Try to go to next page
                try:
                    next_button = sb.find_element("a[aria-label='Next page']")
                    if next_button and next_button.is_enabled():
                        print("➡️ Going to next page...")
                        sb.click(next_button)
                        sb.sleep(3)
                        page_num += 1
                    else:
                        print("❌ No next page available")
                        break
                except Exception as e:
                    print(f"❌ Error navigating to next page: {str(e)}")
                    break
                    
            except Exception as e:
                print(f"❌ Error processing page {page_num}: {str(e)}")
                break
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total CPUs collected: {len(all_cpus)}")
        
        # Save to JSON
        print(f"💾 Saving to JSON: {json_file}")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_cpus, f, indent=2, ensure_ascii=False)
        
        # Save to CSV
        print(f"💾 Saving to CSV: {csv_file}")
        if all_cpus:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_cpus[0].keys())
                writer.writeheader()
                writer.writerows(all_cpus)
        
        print(f"✅ Data saved successfully!")
        print(f"📁 JSON: {json_file}")
        print(f"📁 CSV: {csv_file}")
        
        return all_cpus

if __name__ == "__main__":
    scrape_french_cpus_precise()