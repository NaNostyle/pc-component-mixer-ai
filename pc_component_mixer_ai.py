#!/usr/bin/env python3
"""
PC Component Mixer AI - Enhanced CLI tool with AI-powered deal analysis
Combines PC component data with AI analysis to identify good deals
"""

import json
import argparse
import os
import re
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenRouterAI:
    """OpenRouter AI integration for deal analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Try to load API key from openrouter.txt file first
        api_key_from_file = None
        try:
            with open("openrouter.txt", "r") as f:
                content = f.read().strip()
                if content.startswith("api_key="):
                    api_key_from_file = content.split("=", 1)[1]
        except FileNotFoundError:
            pass
        
        self.api_key = api_key or api_key_from_file or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pc-component-mixer",
            "X-Title": "PC Component Mixer AI"
        }
    
    def analyze_deal(self, product_data: Dict, market_context: str = "") -> Dict[str, Any]:
        """Analyze if a PC component is a good deal using AI"""
        if not self.api_key:
            return {
                "is_good_deal": False,
                "confidence": 0.0,
                "reasoning": "No API key provided",
                "recommendation": "Unable to analyze without API key"
            }
        
        # Prepare product information for AI analysis
        product_info = {
            "name": product_data.get("name", ""),
            "price": product_data.get("price", ""),
            "raw_text": product_data.get("raw_text", ""),
            "url": product_data.get("url", "")
        }
        
        # Create AI prompt for deal analysis
        system_prompt = """You are an expert PC hardware analyst. Analyze PC component deals and determine if they represent good value.

Consider these factors:
1. Component type and specifications
2. Price compared to typical market value
3. Brand reputation and reliability
4. Age and condition (if mentioned)
5. Market trends and availability

Respond with a JSON object containing:
- "is_good_deal": boolean
- "confidence": float (0.0 to 1.0)
- "reasoning": string explaining your analysis
- "recommendation": string with specific advice
- "market_value_estimate": string with estimated fair price range
- "deal_score": integer (1-10, where 10 is exceptional deal)"""

        user_prompt = f"""Analyze this PC component deal:

Product: {product_info['name']}
Price: {product_info['price']}
Details: {product_info['raw_text']}
URL: {product_info['url']}

{market_context}

Is this a good deal? Provide detailed analysis."""

        try:
            payload = {
                "model": "x-ai/grok-4-fast:free",  # Free Grok model
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            ai_response = response.json()
            content = ai_response['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                # Clean the content to extract JSON if it's embedded
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                return {
                    "is_good_deal": "good deal" in content.lower() or "excellent" in content.lower(),
                    "confidence": 0.5,
                    "reasoning": content[:200] + "..." if len(content) > 200 else content,
                    "recommendation": "See reasoning for details",
                    "market_value_estimate": "Unable to determine",
                    "deal_score": 5
                }
                
        except Exception as e:
            return {
                "is_good_deal": False,
                "confidence": 0.0,
                "reasoning": f"AI analysis failed: {str(e)}",
                "recommendation": "Manual review recommended",
                "market_value_estimate": "Unknown",
                "deal_score": 0
            }
    
    def generate_smart_query(self, user_intent: str, available_components: List[str]) -> Dict[str, Any]:
        """Generate smart search parameters based on user intent"""
        if not self.api_key:
            return {
                "keywords": [],
                "components": available_components,
                "price_range": {"min": None, "max": None},
                "reasoning": "No API key provided for smart query generation"
            }
        
        system_prompt = """You are a PC hardware expert. Analyze user intent and generate optimal search parameters for finding PC components.

Return a JSON object with:
- "keywords": array of search keywords
- "components": array of relevant component types
- "price_range": object with "min" and "max" price suggestions
- "reasoning": explanation of your choices"""

        user_prompt = f"""User wants to: {user_intent}

Available component types: {', '.join(available_components)}

Generate smart search parameters to find the best matches."""

        try:
            payload = {
                "model": "x-ai/grok-4-fast:free",  # Free Grok model
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 800
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=20
            )
            response.raise_for_status()
            
            ai_response = response.json()
            content = ai_response['choices'][0]['message']['content']
            
            # Handle empty content (Grok sometimes returns empty content)
            if not content:
                return {
                    "keywords": [],
                    "components": available_components,
                    "price_range": {"min": None, "max": None},
                    "reasoning": "AI returned empty response"
                }
            
            try:
                # Clean the content to extract JSON if it's embedded
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "keywords": [],
                    "components": available_components,
                    "price_range": {"min": None, "max": None},
                    "reasoning": f"AI response parsing failed. Raw response: {content[:100]}..."
                }
                
        except Exception as e:
            return {
                "keywords": [],
                "components": available_components,
                "price_range": {"min": None, "max": None},
                "reasoning": f"Smart query generation failed: {str(e)}"
            }

def load_json_file(filepath: str) -> List[Dict]:
    """Load JSON file and return list of products"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return [data]
    except Exception as e:
        print(f"❌ Error loading {filepath}: {str(e)}")
        return []

def find_component_files() -> Dict[str, List[str]]:
    """Find all available component JSON files"""
    component_types = {
        'case': ['french_cases_precise_*.json'],
        'cpu_cooler': ['french_cpu_coolers_precise_*.json'],
        'cpu': ['french_cpus_precise_*.json'],
        'hard_drive': ['french_internal_hard_drives_precise_*.json'],
        'memory': ['french_memory_precise_*.json'],
        'motherboard': ['french_motherboards_precise_*.json'],
        'graphic_card': ['french_video_cards_precise_*.json'],
        'power_supply': ['french_power_supplies_precise_*.json']
    }
    
    found_files = {}
    for component_type, patterns in component_types.items():
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        if files:
            # Sort by modification time (newest first)
            files.sort(key=os.path.getmtime, reverse=True)
            found_files[component_type] = files
    
    return found_files

def search_products(products: List[Dict], keywords: List[str], min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:
    """Search products by keywords and price range"""
    filtered_products = []
    
    for product in products:
        # Check keywords in raw_text (case insensitive) - ALL keywords must be present
        if keywords:
            raw_text = product.get('raw_text', '').lower()
            # Check that ALL keywords are present in the raw_text
            if not all(keyword.lower() in raw_text for keyword in keywords):
                continue
        
        # Check price range
        if min_price is not None or max_price is not None:
            try:
                price_str = product.get('price', '').replace('€', '').replace(',', '.')
                price = float(price_str)
                
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
            except (ValueError, TypeError):
                continue
        
        filtered_products.append(product)
    
    return filtered_products

def analyze_products_with_ai(products: List[Dict], ai_client: OpenRouterAI, max_products: int = 50) -> List[Dict]:
    """Analyze products with AI and add deal analysis"""
    analyzed_products = []
    
    print(f"🤖 Analyzing {min(len(products), max_products)} products with AI...")
    
    for i, product in enumerate(products[:max_products]):
        print(f"   Analyzing {i+1}/{min(len(products), max_products)}: {product.get('name', 'Unknown')[:50]}...")
        
        # Get AI analysis
        analysis = ai_client.analyze_deal(product)
        
        # Add AI analysis to product
        product_with_analysis = product.copy()
        product_with_analysis['ai_analysis'] = analysis
        
        analyzed_products.append(product_with_analysis)
    
    return analyzed_products

def generate_output_filename(components: List[str], keywords: List[str], min_price: Optional[float], max_price: Optional[float], ai_enhanced: bool = False) -> str:
    """Generate output filename based on parameters"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Component part
    component_part = "_".join(components)
    
    # Keywords part
    keyword_part = ""
    if keywords:
        # Clean keywords for filename
        clean_keywords = [re.sub(r'[^\w]', '', kw) for kw in keywords[:3]]  # Max 3 keywords
        keyword_part = "_" + "_".join(clean_keywords)
    
    # Price part
    price_part = ""
    if min_price is not None or max_price is not None:
        if min_price is not None and max_price is not None:
            price_part = f"_€{min_price:.0f}-{max_price:.0f}"
        elif min_price is not None:
            price_part = f"_€{min_price:.0f}+"
        elif max_price is not None:
            price_part = f"_€{max_price:.0f}-"
    
    # AI enhancement indicator
    ai_part = "_ai" if ai_enhanced else ""
    
    filename = f"pc_mix_{component_part}{keyword_part}{price_part}{ai_part}_{timestamp}.json"
    return filename

def interactive_mode():
    """Interactive CLI mode with AI features"""
    print("🔧 PC Component Mixer AI - Interactive Mode")
    print("=" * 50)
    
    # Initialize AI client
    ai_client = OpenRouterAI()
    if ai_client.api_key:
        print("✅ AI analysis enabled")
    else:
        print("⚠️  AI analysis disabled (no API key)")
    
    # Find available files
    available_files = find_component_files()
    if not available_files:
        print("❌ No component JSON files found!")
        return
    
    print("\n📁 Available component types:")
    for i, (component_type, files) in enumerate(available_files.items(), 1):
        print(f"  {i}. {component_type.replace('_', ' ').title()} ({len(files)} files)")
    
    # Smart query mode
    print("\n🤖 AI-Powered Smart Query (y/n):")
    smart_query = input("> ").strip().lower() == 'y'
    
    if smart_query and ai_client.api_key:
        print("\n💭 Describe what you're looking for:")
        user_intent = input("> ").strip()
        
        if user_intent:
            print("🤖 Generating smart search parameters...")
            smart_params = ai_client.generate_smart_query(user_intent, list(available_files.keys()))
            
            print(f"\n🎯 AI Recommendations:")
            print(f"   Keywords: {', '.join(smart_params['keywords']) if smart_params['keywords'] else 'None'}")
            print(f"   Components: {', '.join(smart_params['components'])}")
            print(f"   Price range: {smart_params['price_range']}")
            print(f"   Reasoning: {smart_params['reasoning']}")
            
            use_ai_params = input("\nUse AI recommendations? (y/n): ").strip().lower() == 'y'
            
            if use_ai_params:
                selected_components = smart_params['components']
                keywords = smart_params['keywords']
                min_price = smart_params['price_range'].get('min')
                max_price = smart_params['price_range'].get('max')
            else:
                # Fall back to manual selection
                selected_components = []
                keywords = []
                min_price = None
                max_price = None
        else:
            smart_query = False
    
    if not smart_query:
        # Manual component selection
        print("\n🎯 Select components to mix (comma-separated numbers, or 'all'):")
        selection = input("> ").strip()
        
        if selection.lower() == 'all':
            selected_components = list(available_files.keys())
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                component_types = list(available_files.keys())
                selected_components = [component_types[i] for i in indices if 0 <= i < len(component_types)]
            except (ValueError, IndexError):
                print("❌ Invalid selection!")
                return
        
        if not selected_components:
            print("❌ No components selected!")
            return
        
        print(f"\n✅ Selected components: {', '.join(selected_components)}")
        
        # Manual keyword search
        print("\n🔍 Enter keywords to search (comma-separated, or press Enter to skip):")
        keywords_input = input("> ").strip()
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()] if keywords_input else []
        
        # Manual price filtering
        print("\n💰 Price filtering (press Enter to skip):")
        min_price_input = input("Minimum price (€): ").strip()
        max_price_input = input("Maximum price (€): ").strip()
        
        min_price = float(min_price_input) if min_price_input else None
        max_price = float(max_price_input) if max_price_input else None
    
    # Load data
    all_products = []
    for component_type in selected_components:
        files = available_files[component_type]
        if files:
            latest_file = files[0]  # Use newest file
            print(f"📂 Loading {component_type} from {latest_file}...")
            products = load_json_file(latest_file)
            all_products.extend(products)
            print(f"   Loaded {len(products)} {component_type} products")
    
    print(f"\n📊 Total products loaded: {len(all_products)}")
    
    # Filter products
    print("\n🔍 Filtering products...")
    filtered_products = search_products(all_products, keywords, min_price, max_price)
    
    print(f"✅ Found {len(filtered_products)} products matching criteria")
    
    if not filtered_products:
        print("❌ No products found matching your criteria!")
        return
    
    # AI analysis
    ai_enhanced = False
    if ai_client.api_key:
        print("\n🤖 Enable AI deal analysis? (y/n):")
        enable_ai = input("> ").strip().lower() == 'y'
        
        if enable_ai:
            max_analyze = min(len(filtered_products), 50)  # Limit to 50 for cost control
            print(f"\n⚠️  Will analyze top {max_analyze} products (API cost consideration)")
            confirm = input("Continue? (y/n): ").strip().lower() == 'y'
            
            if confirm:
                # Sort by price (ascending) to prioritize cheaper items
                filtered_products.sort(key=lambda x: float(x.get('price', '0').replace('€', '').replace(',', '.')))
                analyzed_products = analyze_products_with_ai(filtered_products, ai_client, max_analyze)
                ai_enhanced = True
                
                # Show AI analysis summary
                good_deals = [p for p in analyzed_products if p.get('ai_analysis', {}).get('is_good_deal', False)]
                print(f"\n🎯 AI Analysis Summary:")
                print(f"   Good deals found: {len(good_deals)}")
                print(f"   Average deal score: {sum(p.get('ai_analysis', {}).get('deal_score', 0) for p in analyzed_products) / len(analyzed_products):.1f}/10")
                
                # Show top deals
                if good_deals:
                    print(f"\n🏆 Top AI-Recommended Deals:")
                    for i, product in enumerate(good_deals[:5], 1):
                        analysis = product.get('ai_analysis', {})
                        print(f"   {i}. {product.get('name', 'N/A')[:60]} - {product.get('price', 'N/A')}")
                        print(f"      Deal Score: {analysis.get('deal_score', 0)}/10 - {analysis.get('reasoning', 'No reasoning')[:100]}...")
            else:
                analyzed_products = filtered_products
        else:
            analyzed_products = filtered_products
    else:
        analyzed_products = filtered_products
    
    # Generate output filename
    output_filename = generate_output_filename(selected_components, keywords, min_price, max_price, ai_enhanced)
    
    # Save results
    print(f"\n💾 Saving results to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(analyzed_products, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(analyzed_products)} products to {output_filename}")
    
    # Show sample results
    print(f"\n📋 Sample results (first 5):")
    for i, product in enumerate(analyzed_products[:5], 1):
        ai_info = ""
        if ai_enhanced and 'ai_analysis' in product:
            analysis = product['ai_analysis']
            ai_info = f" [AI Score: {analysis.get('deal_score', 0)}/10]"
        print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}{ai_info}")
    
    if len(analyzed_products) > 5:
        print(f"  ... and {len(analyzed_products) - 5} more")

def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="PC Component Mixer AI - Enhanced tool with AI-powered deal analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with AI
  python pc_component_mixer_ai.py

  # AI-powered smart query
  python pc_component_mixer_ai.py --ai-query "gaming PC under 1000 euros"

  # Command line mode with AI analysis
  python pc_component_mixer_ai.py --components cpu,memory --keywords "intel,ddr4" --ai-analyze

  # Smart query with specific components
  python pc_component_mixer_ai.py --ai-query "budget gaming setup" --components graphic_card,cpu
        """
    )
    
    parser.add_argument(
        '--components', '-c',
        help='Components to mix (comma-separated): case, cpu_cooler, cpu, hard_drive, memory, motherboard, graphic_card, power_supply, or "all"',
        type=str
    )
    
    parser.add_argument(
        '--keywords', '-k',
        help='Keywords to search in raw_text (comma-separated)',
        type=str
    )
    
    parser.add_argument(
        '--min-price', '-min',
        help='Minimum price in euros',
        type=float
    )
    
    parser.add_argument(
        '--max-price', '-max',
        help='Maximum price in euros',
        type=float
    )
    
    parser.add_argument(
        '--ai-query', '-q',
        help='AI-powered smart query (describe what you want)',
        type=str
    )
    
    parser.add_argument(
        '--ai-analyze', '-a',
        action='store_true',
        help='Enable AI deal analysis on results'
    )
    
    parser.add_argument(
        '--max-analyze',
        help='Maximum number of products to analyze with AI (default: 50)',
        type=int,
        default=50
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output filename (auto-generated if not specified)',
        type=str
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode (ignores other arguments)'
    )
    
    args = parser.parse_args()
    
    # If no arguments or interactive flag, run interactive mode
    if args.interactive or not any([args.components, args.keywords, args.min_price, args.max_price, args.ai_query]):
        interactive_mode()
        return
    
    # Command line mode
    print("🔧 PC Component Mixer AI - Command Line Mode")
    print("=" * 50)
    
    # Initialize AI client
    ai_client = OpenRouterAI()
    if ai_client.api_key:
        print("✅ AI analysis enabled")
    else:
        print("⚠️  AI analysis disabled (no API key)")
    
    # Find available files
    available_files = find_component_files()
    if not available_files:
        print("❌ No component JSON files found!")
        return
    
    # Handle AI query
    if args.ai_query:
        print(f"🤖 Processing AI query: '{args.ai_query}'")
        smart_params = ai_client.generate_smart_query(args.ai_query, list(available_files.keys()))
        
        print(f"\n🎯 AI Recommendations:")
        print(f"   Keywords: {', '.join(smart_params['keywords']) if smart_params['keywords'] else 'None'}")
        print(f"   Components: {', '.join(smart_params['components'])}")
        print(f"   Price range: {smart_params['price_range']}")
        print(f"   Reasoning: {smart_params['reasoning']}")
        
        # Use AI recommendations
        selected_components = smart_params['components']
        keywords = smart_params['keywords']
        min_price = smart_params['price_range'].get('min')
        max_price = smart_params['price_range'].get('max')
    else:
        # Parse components manually
        if args.components.lower() == 'all':
            selected_components = list(available_files.keys())
        else:
            selected_components = [comp.strip() for comp in args.components.split(',')]
            # Validate components
            invalid_components = [comp for comp in selected_components if comp not in available_files]
            if invalid_components:
                print(f"❌ Invalid components: {', '.join(invalid_components)}")
                print(f"Available components: {', '.join(available_files.keys())}")
                return
        
        # Parse keywords and prices
        keywords = [kw.strip() for kw in args.keywords.split(',')] if args.keywords else []
        min_price = args.min_price
        max_price = args.max_price
    
    print(f"✅ Selected components: {', '.join(selected_components)}")
    if keywords:
        print(f"🔍 Keywords: {', '.join(keywords)}")
    if min_price is not None or max_price is not None:
        price_range = []
        if min_price is not None:
            price_range.append(f"min: €{min_price}")
        if max_price is not None:
            price_range.append(f"max: €{max_price}")
        print(f"💰 Price range: {', '.join(price_range)}")
    
    # Load data
    all_products = []
    for component_type in selected_components:
        files = available_files[component_type]
        if files:
            latest_file = files[0]  # Use newest file
            print(f"📂 Loading {component_type} from {latest_file}...")
            products = load_json_file(latest_file)
            all_products.extend(products)
            print(f"   Loaded {len(products)} {component_type} products")
    
    print(f"\n📊 Total products loaded: {len(all_products)}")
    
    # Filter products
    print("\n🔍 Filtering products...")
    filtered_products = search_products(all_products, keywords, min_price, max_price)
    
    print(f"✅ Found {len(filtered_products)} products matching criteria")
    
    if not filtered_products:
        print("❌ No products found matching your criteria!")
        return
    
    # AI analysis
    ai_enhanced = False
    if args.ai_analyze and ai_client.api_key:
        max_analyze = min(len(filtered_products), args.max_analyze)
        print(f"\n🤖 Analyzing top {max_analyze} products with AI...")
        
        # Sort by price (ascending) to prioritize cheaper items
        filtered_products.sort(key=lambda x: float(x.get('price', '0').replace('€', '').replace(',', '.')))
        analyzed_products = analyze_products_with_ai(filtered_products, ai_client, max_analyze)
        ai_enhanced = True
        
        # Show AI analysis summary
        good_deals = [p for p in analyzed_products if p.get('ai_analysis', {}).get('is_good_deal', False)]
        print(f"\n🎯 AI Analysis Summary:")
        print(f"   Good deals found: {len(good_deals)}")
        if analyzed_products:
            avg_score = sum(p.get('ai_analysis', {}).get('deal_score', 0) for p in analyzed_products) / len(analyzed_products)
            print(f"   Average deal score: {avg_score:.1f}/10")
    else:
        analyzed_products = filtered_products
    
    # Generate output filename
    if args.output:
        output_filename = args.output
    else:
        output_filename = generate_output_filename(selected_components, keywords, min_price, max_price, ai_enhanced)
    
    # Save results
    print(f"\n💾 Saving results to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(analyzed_products, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(analyzed_products)} products to {output_filename}")
    
    # Show sample results
    print(f"\n📋 Sample results (first 5):")
    for i, product in enumerate(analyzed_products[:5], 1):
        ai_info = ""
        if ai_enhanced and 'ai_analysis' in product:
            analysis = product['ai_analysis']
            ai_info = f" [AI Score: {analysis.get('deal_score', 0)}/10]"
        print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}{ai_info}")
    
    if len(analyzed_products) > 5:
        print(f"  ... and {len(analyzed_products) - 5} more")

if __name__ == "__main__":
    main()