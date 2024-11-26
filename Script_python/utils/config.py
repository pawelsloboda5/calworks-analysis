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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('processing.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class PathsConfig(TypedDict):
    household_data: str
    person_data: str
    output_dir: str
    plots_dir: str
    eligible_households: str
    eligible_persons: str

class Config(TypedDict):
    paths: PathsConfig
    sf_puma_codes: List[int]
    mbsac_thresholds: Dict[int, int]

def load_config(config_path: str = 'Script_python/config.yaml') -> Config:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            loaded_config: Config = yaml.safe_load(f)  # type: ignore
            return loaded_config
    except FileNotFoundError:
        # Default configuration with absolute paths
        project_root = Path(__file__).parent.parent.parent
        default_config: Config = {
            'paths': {
                'household_data': str(project_root / 'Script_python/data/hca_2022.csv'),
                'person_data': str(project_root / 'Script_python/data/pca_2022.csv'),
                'eligible_households': str(project_root / 'Script_python/data/eligible_calworks_sf_households.csv'),
                'eligible_persons': str(project_root / 'Script_python/data/eligible_calworks_sf_persons.csv'),
                'output_dir': str(project_root / 'Script_python/output'),
                'plots_dir': str(project_root / 'Script_python/output/plots')
            },
            'sf_puma_codes': [7507, 7508, 7509, 7510, 7511, 7512, 7513, 7514],
            'mbsac_thresholds': {
                1: 899, 2: 1476, 3: 1829, 4: 2170, 5: 2476,
                6: 2785, 7: 3061, 8: 3331, 9: 3614, 10: 3922
            }
        }
        return default_config 