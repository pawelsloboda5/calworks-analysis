# 📊 CalWORKs Analysis for San Francisco

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://github.com/pawelsloboda5/calworks-analysis/actions/workflows/python-app.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/pawelsloboda5/calworks-analysis)
![Last Commit](https://img.shields.io/github/last-commit/pawelsloboda5/calworks-analysis)

<div align="center">

**A comprehensive data analysis toolkit for examining CalWORKs eligibility and regional affordability across San Francisco's PUMA regions.**

[Key Features](#-key-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

## 🌟 Key Features

- **Automated Eligibility Analysis**: Determine CalWORKs eligibility based on multiple criteria
- **Regional Insights**: Deep analysis of San Francisco's PUMA regions (7507-7514)
- **Income Analysis**: Multi-source income distribution and patterns
- **Housing Affordability**: Detailed rent burden analysis
- **Interactive Visualizations**: Comprehensive data visualization suite

## 📊 Latest Analysis Results

### Employment Rates by Region
- Highest: PUMA 7513 (71.7%)
- Lowest: PUMA 7509 (36.4%)
- Average: ~52.8%

### Income Distribution
- Highest median income: PUMA 7512 ($8,033/month)
- Lowest median income: PUMA 7509 ($1,350/month)
- Significant income inequality in regions 7512 and 7513

### Housing Affordability
- Most affordable: PUMA 7513 (24% rent-to-income ratio)
- Least affordable: PUMA 7508 (93% rent-to-income ratio)

## 🚀 Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/pawelsloboda5/calworks-analysis.git
cd calworks-analysis
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Prepare Data**
- Place PUMS data files in `Script_python/data/`:
  - `hca_2022.csv` (Household data)
  - `pca_2022.csv` (Person data)

3. **Run Analysis**
```bash
python Script_python/main.py
```

## 📈 Visualization Examples

<table>
<tr>
<td>
<img src="docs/images/income_distribution.png" alt="Income Distribution" width="400"/>
<br>
<em>Income Distribution by Region</em>
</td>
<td>
<img src="docs/images/employment_rate.png" alt="Employment Rate" width="400"/>
<br>
<em>Employment Rates</em>
</td>
</tr>
</table>

## 🛠️ Technology Stack

- **Data Processing**: pandas, numpy
- **Statistical Analysis**: scipy
- **Visualization**: matplotlib, seaborn
- **Configuration**: PyYAML
- **Testing**: pytest, coverage

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Data Requirements](docs/data_requirements.md)
- [Analysis Methods](docs/analysis_methods.md)
- [API Reference](docs/api_reference.md)
- [Technical Specifications](docs/technical_specifications.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Data source: U.S. Census Bureau's Public Use Microdata Sample (PUMS)
- Analysis focuses on San Francisco PUMA regions: 7507-7514
- Special thanks to all contributors and maintainers

## 📧 Contact

Pawel Sloboda - [pawelsloboda5@gmail.com](mailto:pawelsloboda5@gmail.com)

Project Link: [https://github.com/pawelsloboda5/calworks-analysis](https://github.com/pawelsloboda5/calworks-analysis)

---
<div align="center">
Made with ❤️ for the San Francisco community
</div> 