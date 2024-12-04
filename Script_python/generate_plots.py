from pathlib import Path
import pandas as pd
from Script_python.utils.config import load_config
from Script_python.visualizations.plots import generate_summary_plots
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load configuration
        config = load_config()
        
        # Load the analysis results
        output_dir = Path(config["paths"]["output_dir"])
        region_analysis_path = output_dir / "region_analysis.csv"
        
        # Check if the analysis file exists
        if not region_analysis_path.exists():
            raise FileNotFoundError(
                "Analysis results not found. Please run the full pipeline first using main.py"
            )
        
        # Load the data
        region_summary = pd.read_csv(region_analysis_path)
        
        # Generate plots
        plots_dir = Path(config["paths"]["plots_dir"])
        logger.info("Starting plot generation...")
        generate_summary_plots(region_summary, plots_dir)
        logger.info("Successfully generated all plots")
    except Exception as e:
        logger.error(f"Error generating plots: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 