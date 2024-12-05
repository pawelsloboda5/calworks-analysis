# /utils/config.py
# This file contains the configuration for the project.
# It is used to load the configuration from the YAML file and provide default values if the file is not found.
from typing import Dict, List, Union, TypedDict

import logging
from pathlib import Path

import yaml


def setup_logging() -> logging.Logger:
    """Configure logging for all scripts."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("processing.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


class PathsConfig(TypedDict):
    household_data: Path
    person_data: Path
    output_dir: Path
    plots_dir: Path
    eligible_households: Path
    eligible_persons: Path


class Config(TypedDict):
    paths: PathsConfig
    sf_puma_codes: List[int]
    mbsac_thresholds: Dict[int, int]


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load and validate configuration."""
    try:
        # Load YAML relative to Script_python directory
        config_file = Path(__file__).parent.parent / config_path
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Convert all paths to Path objects
        for key, value in config["paths"].items():
            config["paths"][key] = Path(value)
            
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_path}")
