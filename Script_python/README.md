# 📊 CalWORKs Data Analysis for San Francisco

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-yellow)

A comprehensive data analysis tool for examining CalWORKs eligibility and regional affordability across San Francisco's PUMA regions. This project processes PUMS (Public Use Microdata Sample) data to provide insights into income distribution, employment patterns, and housing affordability.

## 📈 Key Findings

Based on our analysis of San Francisco PUMA regions (7507-7514):

1. **Employment Rates**:
   - Highest: PUMA 7513 (71.7%)
   - Lowest: PUMA 7509 (36.4%)
   - Average across regions: ~52.8%

2. **Income Distribution**:
   - Highest median income: PUMA 7512 ($8,033/month)
   - Lowest median income: PUMA 7509 ($1,350/month)
   - Significant income inequality in regions 7512 and 7513

3. **Rent Burden**:
   - Most affordable: PUMA 7513 (24% rent-to-income ratio)
   - Least affordable: PUMA 7508 (93% rent-to-income ratio)

4. **Population Distribution**:
   - Largest eligible population: PUMA 7507 (277 people)
   - Smallest eligible population: PUMA 7511 (110 people)

## 🚀 Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/pawelsloboda/calworks-analysis.git
cd calworks-analysis
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Prepare Data**
Place your PUMS data files in `Script_python/data/`:
- `hca_2022.csv` (Household data)
- `pca_2022.csv` (Person data)

3. **Run Analysis**
```bash
python Script_python/main.py
```

## 📊 Generated Visualizations

Our analysis produces four key visualizations:

1. **Income Distribution by Region**
   - Box plots showing income spread
   - Median income markers
   - Regional comparisons

2. **Employment Rate Analysis**
   - Employment rates by PUMA
   - Income source distribution
   - Regional employment patterns

3. **Housing Affordability**
   - Rent burden percentages
   - Affordability metrics
   - Regional comparisons

4. **Demographic Analysis**
   - Household sizes
   - Population distribution
   - Regional demographics

## 🛠️ Configuration

Customize the analysis in `config.yaml`:
```yaml
paths:
  household_data: 'data/hca_2022.csv'
  person_data: 'data/pca_2022.csv'
  output_dir: 'output'

analysis:
  min_household_size: 1
  max_household_size: 10
  income_percentile_cutoff: 95
```

## 🤝 Documentation

- [Installation Guide](docs/installation.md)
- [Data Requirements](docs/data_requirements.md)
- [Analysis Methods](docs/analysis_methods.md)
- [API Reference](docs/api_reference.md)

## 🤝 Contributing

Contributions welcome! See our [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 📧 Contact

Pawel Sloboda - [pawelsloboda5@gmail.com](mailto:pawelsloboda5@gmail.com)

Project Link: [https://github.com/pawelsloboda/calworks-analysis](https://github.com/pawelsloboda/calworks-analysis)

---
<p align="center">
Made with ❤️ for the San Francisco community
</p>

