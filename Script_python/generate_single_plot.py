import pandas as pd
from pathlib import Path
from Script_python.utils.config import load_config
from Script_python.visualizations.plots import (
    plot_eligibility_by_region,
    setup_plot_style
)

def generate_single_plot():
    config = load_config()
    output_dir = Path(config["paths"]["output_dir"])
    region_analysis_path = output_dir / "region_analysis.csv"
    
    if not region_analysis_path.exists():
        raise FileNotFoundError(
            "Analysis results not found. Please run the full pipeline first using main.py"
        )
    
    region_summary = pd.read_csv(region_analysis_path)
    plots_dir = Path(config["paths"]["plots_dir"])
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate just the eligibility by region plot
    plot_eligibility_by_region(region_summary, plots_dir)
    
    print(f"Plot has been generated in: {plots_dir}")

if __name__ == "__main__":
    generate_single_plot() 