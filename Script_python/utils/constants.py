from pathlib import Path

# Project structure constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'Script_python/data'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True) 