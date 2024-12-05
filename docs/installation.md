# Installation Guide

## System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- 1GB free disk space

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pawelsloboda/calworks-analysis.git
cd calworks-analysis
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Data Directories
```bash
# Create necessary directories
mkdir -p Script_python/data/
mkdir -p Script_python/after_main_run_logs/
```

### 4. Data Setup
- Place household data (hca_2022.csv) in Script_python/data/
- Place person data (pca_2022.csv) in Script_python/data/
- Update config.yaml with correct file paths

### 5. Verify Installation
```bash
# Run tests
pytest

# Run pipeline
python run_analysis.py
```

## Troubleshooting

### Common Issues

1. **Plotly Visualization Errors**
   ```
   Solution: Ensure plotly and its dependencies are installed
   pip install plotly kaleido
   ```

2. **Missing Dependencies**
   ```
   Solution: Run pip install -r requirements.txt again
   ```

3. **Data Directory Issues**
   ```
   Solution: Check file permissions and paths in config.yaml
   ```

## Updating

To update to the latest version:
```bash
git pull origin main
pip install -r requirements.txt
``` 