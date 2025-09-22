# PC Component Mixer AI 🤖

An AI-powered PC component scraper and mixer that helps you find the best deals on computer components from French marketplaces. This tool combines web scraping, data analysis, and AI-powered deal assessment to help you make informed purchasing decisions.

## 🚀 Features

### 🔍 Comprehensive Component Scraping
- **CPU Processors**: Intel and AMD processors with detailed specifications
- **Graphics Cards**: NVIDIA and AMD graphics cards with performance metrics
- **Memory (RAM)**: DDR4/DDR5 memory modules with speed and capacity info
- **Motherboards**: Compatible motherboards with socket and chipset details
- **Storage**: Internal hard drives and SSDs with capacity and speed data
- **Power Supplies**: PSUs with wattage and efficiency ratings
- **Cases**: PC cases with form factor and compatibility info
- **CPU Coolers**: Air and liquid cooling solutions

### 🤖 AI-Powered Deal Analysis
- Analyzes PC component deals using advanced AI models
- Provides deal scores (1-10) and confidence ratings
- Explains reasoning behind recommendations
- Estimates market value and suggests fair price ranges

### 🧠 Smart Query Generation
- Natural language queries (e.g., "gaming PC under 1000 euros")
- AI automatically generates optimal search parameters
- Intelligent component and keyword suggestions
- Price range recommendations based on user intent

### 📊 Data Sources
- **LeBonCoin**: French marketplace with extensive component listings
- **PCPartPicker**: International component database and compatibility
- **Vinted**: Additional marketplace for used components

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NaNostyle/pc-component-mixer-ai.git
   cd pc-component-mixer-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_ai.txt
   ```

3. **Set up OpenRouter API key** (for AI features):
   - Get your API key from [OpenRouter](https://openrouter.ai/)
   - Create a `.env` file with your API key:
     ```
     OPENROUTER_API_KEY=your_actual_api_key_here
     ```

## 🎯 Usage Examples

### Interactive Mode with AI
```bash
python pc_component_mixer_ai.py
```
- Choose AI-powered smart query mode
- Describe what you're looking for in natural language
- Get AI recommendations for components, keywords, and price ranges
- Enable AI deal analysis on results

### AI Smart Query
```bash
python pc_component_mixer_ai.py --ai-query "budget gaming setup under 800 euros"
```

### Command Line with AI Analysis
```bash
python pc_component_mixer_ai.py --components cpu,graphic_card --keywords "intel,nvidia" --ai-analyze
```

### Scraping Individual Components
```bash
# Scrape CPUs
python french_cpu_precise.py

# Scrape Graphics Cards
python french_video_card_precise.py

# Scrape Memory
python french_memory_precise.py
```

## 🔧 Command Line Options

### AI-Specific Options
- `--ai-query, -q`: Natural language query for AI to interpret
- `--ai-analyze, -a`: Enable AI deal analysis on results
- `--max-analyze`: Maximum products to analyze (default: 50)

### General Options
- `--components, -c`: Component types to include
- `--keywords, -k`: Search keywords
- `--min-price, -min`: Minimum price filter
- `--max-price, -max`: Maximum price filter
- `--output, -o`: Custom output filename
- `--interactive, -i`: Interactive mode

## 📋 Output Format

Each analyzed product includes comprehensive data:

```json
{
  "name": "Intel Core i7-12700K",
  "price": "€299.99",
  "raw_text": "...",
  "ai_analysis": {
    "is_good_deal": true,
    "confidence": 0.85,
    "reasoning": "Excellent price for a high-performance CPU...",
    "recommendation": "Strong buy - great value for gaming and productivity",
    "market_value_estimate": "€320-350",
    "deal_score": 8
  }
}
```

## 🏗️ Project Structure

```
pc-component-mixer-ai/
├── pc_component_mixer_ai.py      # Main AI-enhanced mixer
├── pc_component_mixer.py         # Original mixer (no AI)
├── french_*_precise.py           # Individual component scrapers
├── leboncoin_scraper.py          # LeBonCoin marketplace scraper
├── pcpartpicker_scraper.py       # PCPartPicker scraper
├── vinted_scraper.py             # Vinted marketplace scraper
├── requirements_ai.txt           # AI dependencies
├── requirements.txt              # Basic dependencies
└── *.csv, *.json                 # Scraped data files
```

## 💡 AI Features Explained

### Deal Analysis
- **Deal Score**: 1-10 rating (10 = exceptional deal)
- **Confidence**: 0.0-1.0 confidence in the analysis
- **Reasoning**: Detailed explanation of the assessment
- **Recommendation**: Specific buying advice
- **Market Value**: Estimated fair price range

### Smart Query
- Interprets natural language requests
- Suggests relevant component types
- Generates appropriate keywords
- Recommends price ranges
- Provides reasoning for suggestions

## ⚠️ Important Notes

### API Costs
- AI analysis uses OpenRouter API (costs apply)
- Default limit: 50 products per analysis
- Use `--max-analyze` to control costs
- Smart queries are free (no analysis cost)

### Performance
- AI analysis adds processing time
- Results are cached in output files
- Consider analyzing subsets for large datasets

### Accuracy
- AI analysis is for guidance only
- Always verify prices and specifications
- Market conditions change rapidly
- Use as one factor in decision-making

## 🎯 Use Cases

### For Buyers
- Find the best deals automatically
- Get expert analysis on component value
- Discover components matching your needs
- Compare market prices with AI insights

### For Sellers
- Price your components competitively
- Understand market positioning
- Identify undervalued listings
- Get pricing recommendations

### For Researchers
- Analyze market trends
- Study pricing patterns
- Compare component values
- Generate market reports

## 🚀 Getting Started

1. **Install and configure** (see Installation above)
2. **Try interactive mode**: `python pc_component_mixer_ai.py`
3. **Test smart query**: Use natural language to describe what you want
4. **Enable AI analysis**: Get deal scores and recommendations
5. **Review results**: Check AI insights in the output JSON

## 📞 Support

- OpenRouter API documentation: https://openrouter.ai/docs
- Issues and questions: Create an issue in the repository
- For basic usage without AI: See `pc_component_mixer.py`

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This tool is for educational and research purposes. Always respect website terms of service and rate limits when scraping data.