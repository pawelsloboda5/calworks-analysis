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
mkdir -p Script_python/output/
```

### 4. Verify Installation
```bash
# Run tests
pytest

# Run sample analysis
python Script_python/main.py --test
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   Solution: Ensure you're in the correct directory and virtual environment is activated
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