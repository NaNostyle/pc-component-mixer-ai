#!/usr/bin/env python3
"""
PC Part Picker Scraper Runner
Author: AI Assistant
Description: Command-line interface for running the PC Part Picker scrapers
"""

import argparse
import sys
import json
from typing import Optional

def run_seleniumbase_scraper(component: Optional[str] = None, pages: int = 2, output_format: str = "both"):
    """Run the SeleniumBase scraper with Cloudflare bypass"""
    try:
        from seleniumbase import SB
        from datetime import datetime
        import csv
        
        print("🚀 Starting SeleniumBase scraper with Cloudflare bypass...")
        
        def run_scraper():
            with SB(uc=True, test=True, locale="en") as sb:
                # URL to scrape
                if component:
                    url = f"https://pcpartpicker.com/products/{component}/"
                else:
                    url = "https://pcpartpicker.com/products/cpu/"  # Default to CPU
                
                print(f"🔓 Opening {url} with Cloudflare bypass...")
                sb.uc_open_with_reconnect(url, reconnect_time=3)
                
                # Handle CAPTCHA
                try:
                    sb.uc_gui_click_captcha()
                    print("✅ CAPTCHA handled successfully")
                except:
                    print("ℹ️ No CAPTCHA detected")
                
                sb.sleep(3)
                
                # Find product names
                all_elements = sb.find_elements("*")
                product_names = []
                
                for element in all_elements:
                    try:
                        text = element.text.strip()
                        if text and len(text) > 5 and len(text) < 100:
                            # Look for product names based on component type
                            if component == "cpu":
                                patterns = ["intel core", "amd ryzen", "intel xeon", "amd athlon", "intel pentium", "amd a", "intel celeron", "amd fx"]
                            elif component == "motherboard":
                                patterns = ["asus", "msi", "gigabyte", "asrock", "evga", "biostar", "motherboard", "z790", "b650", "x670"]
                            elif component == "memory":
                                patterns = ["corsair", "g.skill", "kingston", "crucial", "patriot", "team", "memory", "ram", "ddr4", "ddr5"]
                            elif component == "video-card":
                                patterns = ["nvidia", "amd", "geforce", "radeon", "rtx", "gtx", "rx", "video card", "graphics card"]
                            else:
                                patterns = ["intel", "amd", "asus", "msi", "gigabyte", "corsair", "nvidia", "radeon"]
                            
                            if any(pattern in text.lower() for pattern in patterns):
                                if not any(spec in text.lower() for spec in [
                                    "ghz", "mhz", "mb", "gb", "w", "tdp", "cores", "threads"
                                ]):
                                    product_names.append(text)
                    except:
                        continue
                
                unique_products = list(set(product_names))
                unique_products.sort()
                
                if unique_products:
                    print(f"✅ Found {len(unique_products)} unique product names")
                    
                    # Save results
                    results = []
                    for name in unique_products:
                        results.append({
                            "name": name,
                            "category": component or "cpu",
                            "scraped_at": datetime.now().isoformat(),
                            "method": "seleniumbase_cloudflare_bypass"
                        })
                    
                    # Save to files
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = f"pcpartpicker_seleniumbase_{timestamp}.json"
                    csv_file = f"pcpartpicker_seleniumbase_{timestamp}.csv"
                    
                    if output_format in ["json", "both"]:
                        with open(json_file, "w", encoding="utf-8") as f:
                            json.dump(results, f, indent=2, ensure_ascii=False)
                        print(f"💾 Saved to {json_file}")
                    
                    if output_format in ["csv", "both"]:
                        with open(csv_file, "w", newline="", encoding="utf-8") as f:
                            if results:
                                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                                writer.writeheader()
                                writer.writerows(results)
                        print(f"💾 Saved to {csv_file}")
                    
                    return len(results)
                else:
                    print("ℹ️ No product names found")
                    return 0
        
        # Run the scraper
        count = run_scraper()
        print(f"\n📊 Summary: Scraped {count} products using SeleniumBase with Cloudflare bypass")
            
    except ImportError as e:
        print(f"❌ Error importing SeleniumBase: {str(e)}")
        print("💡 Make sure seleniumbase is installed: pip install seleniumbase")
    except Exception as e:
        print(f"❌ Error running SeleniumBase scraper: {str(e)}")

def run_simple_scraper(component: Optional[str] = None, output_format: str = "both"):
    """Run the simple API scraper"""
    try:
        from pcpartpicker_simple import SimplePCPartPickerScraper
        
        print("🚀 Starting simple API scraper...")
        scraper = SimplePCPartPickerScraper(region="us")
        
        if component:
            print(f"🔍 Scraping {component} components...")
            scraper.scrape_component_type(component)
        else:
            print("🔍 Scraping all components...")
            scraper.scrape_all_components()
        
        # Save data
        if output_format in ["csv", "both"]:
            scraper.save_to_csv()
        if output_format in ["json", "both"]:
            scraper.save_to_json()
        
        # Show summary
        stats = scraper.get_summary_stats()
        print(f"\n📊 Summary: {json.dumps(stats, indent=2)}")
        
    except ImportError as e:
        print(f"❌ Error importing simple scraper: {str(e)}")
        print("💡 Make sure pcpartpicker is installed: pip install pcpartpicker")
    except Exception as e:
        print(f"❌ Error running simple scraper: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="PC Part Picker Scraper")
    parser.add_argument(
        "--method", 
        choices=["seleniumbase", "simple", "both"], 
        default="simple",
        help="Scraping method to use"
    )
    parser.add_argument(
        "--component", 
        choices=["cpu", "motherboard", "memory", "storage", "video-card", "case", "power-supply"],
        help="Specific component to scrape (optional)"
    )
    parser.add_argument(
        "--pages", 
        type=int, 
        default=2,
        help="Maximum pages to scrape per category (SeleniumBase only)"
    )
    parser.add_argument(
        "--output", 
        choices=["csv", "json", "both"], 
        default="both",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    print("🖥️ PC Part Picker Scraper")
    print("=" * 50)
    
    if args.method in ["simple", "both"]:
        print("\n📦 Running Simple API Scraper...")
        run_simple_scraper(args.component, args.output)
    
    if args.method in ["seleniumbase", "both"]:
        print("\n🌐 Running SeleniumBase Scraper...")
        run_seleniumbase_scraper(args.component, args.pages, args.output)
    
    print("\n✅ Scraping complete!")

if __name__ == "__main__":
    main()