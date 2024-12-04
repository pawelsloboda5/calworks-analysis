import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Script_python.preprocessing import (
    aggregate_person_data,
    calculate_eligibility,
    load_pums_data,
)
from Script_python.utils.config import load_config, setup_logging
from Script_python.visualizations.plots import generate_summary_plots

def main():
    try:
        # Initialize logging and configuration
        logger = setup_logging()
        config = load_config()

        # Create output directories
        output_dir = Path(config["paths"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        plots_dir = Path(config["paths"]["plots_dir"])
        plots_dir.mkdir(parents=True, exist_ok=True)

        # Load and process data
        household_df, person_df = load_pums_data(
            config["paths"]["household_data"], 
            config["paths"]["person_data"]
        )

        # Run analysis
        logger.info("Starting analysis...")
        # ... rest of your analysis code ...

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 