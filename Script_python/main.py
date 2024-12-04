# Script_python/main.py
"""
Main entry point for the CalWORKs Data Analysis pipeline.
Runs the complete analysis workflow in sequence:
1. Preprocessing (household and person data)
2. Get eligible persons
3. Income filtering and metrics
4. Regional affordability analysis
5. Generate visualizations
"""
import sys
from pathlib import Path
import logging
from datetime import datetime

from Script_python.preprocessing import (
    aggregate_person_data,
    calculate_eligibility,
    load_pums_data,
)
from Script_python.utils.config import load_config, setup_logging
from Script_python.utils.data_ops import validate_eligibility_data
from Script_python.income_filtering import calculate_income_metrics
from Script_python.regions_afford import analyze_regions
from Script_python.visualizations.plots import (
    generate_summary_plots,
    plot_eligibility_breakdown,
    plot_income_distribution
)

def run_pipeline() -> int:
    """Execute the complete analysis pipeline."""
    start_time = datetime.now()
    try:
        # Initialize logging and configuration
        logger = setup_logging()
        config = load_config()
        logger.info("Starting CalWORKs Analysis Pipeline")

        # Create output directories
        output_dir = Path(config["paths"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        plots_dir = Path(config["paths"]["plots_dir"])
        plots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Load and Preprocess Data
        logger.info("Step 1: Loading and preprocessing PUMS data...")
        household_df, person_df = load_pums_data(
            config["paths"]["household_data"],
            config["paths"]["person_data"]
        )
        logger.info(f"Loaded {len(household_df)} households and {len(person_df)} persons")

        # Step 2: Calculate Income Metrics
        logger.info("Step 2: Calculating income metrics...")
        households_with_income, persons_with_income = calculate_income_metrics(config)
        logger.info(f"Processed income for {len(households_with_income)} households and {len(persons_with_income)} persons")

        # Validate data before eligibility calculation
        validate_eligibility_data(household_df)

        # Step 3: Aggregate Person Data 
        logger.info("Step 3: Aggregating person-level data...")
        aggregated_person_df = aggregate_person_data(person_df)        

        # Step 4: Calculate Eligibility
        logger.info("Step 4: Determining CalWORKs eligibility...")
        eligible_households = calculate_eligibility(
            household_df,
            aggregated_person_df,
            config
        )

        # Save eligible households
        eligible_path = output_dir / "eligible_calworks_sf_households.csv"
        eligible_households.to_csv(eligible_path, index=False)
        logger.info(f"Saved eligible households to {eligible_path}")

        # Step 5: Regional Analysis
        logger.info("Step 5: Analyzing regions...")
        region_summary = analyze_regions(eligible_households, person_df)
        region_summary.to_csv(output_dir / "region_analysis.csv", index=False)

        # Step 6: Generate Visualizations
        logger.info("Step 6: Generating visualizations...")
        generate_summary_plots(region_summary, plots_dir)
        plot_eligibility_breakdown(eligible_households, plots_dir)
        plot_income_distribution(region_summary, plots_dir)

        # Print Summary Statistics
        print("\nAnalysis Summary:")
        print(f"Total Households Analyzed: {len(household_df):,}")
        print(f"Eligible Households: {len(eligible_households):,}")
        print(f"Eligibility Rate: {(len(eligible_households)/len(household_df)*100):.1f}%")
        
        # Calculate processing time
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Pipeline completed successfully in {duration}")
        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_pipeline())
