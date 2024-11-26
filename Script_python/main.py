#Script_python/main.py
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
from utils.config import setup_logging, load_config
from utils.data_ops import validate_dataframe
from visualizations.plots import generate_summary_plots

def run_pipeline():
    """Execute the complete analysis pipeline."""
    # Initialize logging and configuration
    logger = setup_logging()
    config = load_config()
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(config['paths']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Preprocessing
        logger.info("Step 1: Preprocessing PUMS data...")
        from preprocessing import load_pums_data, aggregate_person_data, calculate_eligibility
        
        # Load and preprocess data
        household_df, person_df = load_pums_data(
            config['paths']['household_data'],
            config['paths']['person_data']
        )
        
        # Aggregate person data first
        aggregated_person_df = aggregate_person_data(person_df)
        
        # Calculate eligibility using aggregated person data
        eligible_households = calculate_eligibility(household_df, aggregated_person_df)
        
        # Save eligible households
        eligible_households.to_csv(config['paths']['eligible_households'], index=False)
        
        # Step 2: Get eligible persons
        logger.info("Step 2: Filtering eligible persons...")
        from get_eligible_persons import save_eligible_persons
        eligible_persons = save_eligible_persons(person_df, eligible_households)
        eligible_persons.to_csv(config['paths']['eligible_persons'], index=False)
        
        # Step 3: Income filtering
        logger.info("Step 3: Calculating income metrics...")
        from income_filtering import calculate_income_metrics
        households_with_income = calculate_income_metrics(config)
        households_with_income.to_csv(output_dir / 'filtered_income_metrics_households.csv', index=False)
        
        # Step 4: Regional analysis
        logger.info("Step 4: Analyzing regions...")
        from regions_afford import analyze_regions
        region_summary = analyze_regions(households_with_income, eligible_persons)
        region_summary.to_csv(output_dir / 'region_analysis.csv', index=False)
        
        # Step 5: Generate visualizations
        logger.info("Step 5: Generating visualizations...")
        plots_dir = Path(config['paths']['plots_dir'])
        plots_dir.mkdir(parents=True, exist_ok=True)
        generate_summary_plots(region_summary, plots_dir)
        
        logger.info("Analysis pipeline completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_pipeline())