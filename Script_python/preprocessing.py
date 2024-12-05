# Step 1: Preprocess PUMS Data
# Location: Script_python/preprocessing.py
#
from pathlib import Path
from typing import Tuple
from datetime import datetime
import json

import numpy as np
import pandas as pd
from Script_python.utils.config import load_config, setup_logging
from Script_python.utils.data_ops import safe_numeric_conversion, validate_dataframe

# Setup logging and load config
logger = setup_logging()
config = load_config()


def load_pums_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and filter PUMS data for California."""
    config = load_config()
    
    # Load raw data
    household_df = pd.read_csv(config["paths"]["household_data"], low_memory=False)
    person_df = pd.read_csv(config["paths"]["person_data"], low_memory=False)
    
    logger.info(f"Raw data shapes - Households: {household_df.shape}, Persons: {person_df.shape}")
    
    # Filter for California
    state_code = config["pipeline"]["state_code"]
    household_df = household_df[household_df["ST"] == state_code].copy()
    
    # Filter persons based on household SERIALNO
    valid_serialnos = set(household_df["SERIALNO"])
    person_df = person_df[person_df["SERIALNO"].isin(valid_serialnos)].copy()

    # Add monthly income columns to household_df
    household_df['monthly_income'] = household_df['HINCP'] / 12
    
    # Calculate MBSAC thresholds for all households
    household_df['MBSAC'] = household_df['NP'].apply(
        lambda x: calculate_mbsac_threshold(x, config)
    )
    
    # Create monthly versions of all income columns in person_df
    income_cols = ['PAP', 'RETP', 'INTP', 'SSP']
    for col in income_cols:
        if col in person_df.columns:
            person_df[f'monthly_{col}'] = person_df[col] / 12
            logger.info(f"Created monthly_{col} from {col}")
        else:
            logger.warning(f"Income column {col} not found in person data")
            person_df[col] = 0
            person_df[f'monthly_{col}'] = 0
    
    # Add total earned income if available
    if 'WAGP' in person_df.columns and 'SEMP' in person_df.columns:
        person_df['total_earned_income'] = person_df['WAGP'].fillna(0) + person_df['SEMP'].fillna(0)
        person_df['monthly_earned_income'] = person_df['total_earned_income'] / 12
        logger.info("Created monthly_earned_income from WAGP + SEMP")
    
    logger.info(f"After state filtering - Households: {len(household_df)}, Persons: {len(person_df)}")
    
    return household_df, person_df


def aggregate_person_data(person_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate person-level data to household level using SERIALNO.
    """
    try:
        # Debug: Print shape and columns before aggregation
        logger.info(f"Person data shape before aggregation: {person_df.shape}")
        logger.info(f"Columns available: {person_df.columns.tolist()}")

        # Ensure PAP is numeric and filled with 0s
        person_df["PAP"] = pd.to_numeric(person_df["PAP"], errors="coerce").fillna(0)

        # Aggregate with proper column names
        aggregated_person_df = (
            person_df.groupby("SERIALNO")
            .agg(
                PAP=("PAP", "sum"),
                any_pap=("PAP", lambda x: (x > 0).any())
            )
            .reset_index()
        )
        
        # Convert boolean to numeric
        aggregated_person_df["any_pap"] = aggregated_person_df["any_pap"].astype(int)
        
        return aggregated_person_df

    except Exception as e:
        logger.error(f"Error aggregating person data: {str(e)}")
        raise


def calculate_mbsac_threshold(household_size: int, config: dict) -> float:
    """Calculate MBSAC threshold for a given household size."""
    if household_size <= 0:
        # Don't log individual warnings, this will be handled at the DataFrame level
        return config['mbsac_thresholds'][1]
    
    if household_size <= 10:
        return config['mbsac_thresholds'][household_size]
    else:
        # For households larger than 10, add additional person amount
        base_amount = config['mbsac_thresholds'][10]
        extra_persons = household_size - 10
        return base_amount + (extra_persons * config['mbsac_thresholds']['additional_person'])

def calculate_eligibility(
    household_df: pd.DataFrame,
    aggregated_person_df: pd.DataFrame,
    config: dict
) -> pd.DataFrame:
    """
    Determine eligibility for CalWORKs using vectorized operations.
    
    Key Eligibility Criteria:
    1. Income Test: Total countable income < MBSAC threshold
    2. Categorical Eligibility: 
       - Receives Food Stamps (FS = 1)
       - Receives Public Assistance (PAP > 0)
    """
    try:
        # Merge household data with aggregated person data
        household_df = pd.merge(
            household_df,
            aggregated_person_df,
            on="SERIALNO",
            how="left"
        )

        # Calculate MBSAC thresholds
        household_df['MBSAC'] = household_df['NP'].apply(
            lambda x: calculate_mbsac_threshold(x, config)
        )

        # Calculate monthly income (annual / 12)
        household_df['monthly_countable_income'] = household_df['total_countable_income'] / 12

        # Calculate income eligibility (using monthly values)
        household_df['income_eligible'] = (
            (household_df['monthly_countable_income'] < household_df['MBSAC']) |
            (household_df['monthly_countable_income'] == 0)  # Explicitly include zero income households
        )

        # Track eligibility reasons
        fs_col = config['categorical_eligibility']['food_stamps_col']
        pa_col = config['categorical_eligibility']['public_assistance_col']
        
        household_df['food_stamps_receipent'] = household_df[fs_col] == 1
        household_df['public_assistance_receipent'] = household_df[pa_col] > 0

        # Final eligibility determination
        household_df['eligible_calworks'] = (
            household_df['income_eligible'] |
            household_df['food_stamps_receipent'] |
            household_df['public_assistance_receipent']
        )

        # Calculate eligibility statistics
        total_eligible = len(household_df[household_df['eligible_calworks']])
        zero_income_households = len(household_df[household_df['monthly_countable_income'] == 0])
        logger.info(f"Total eligible households: {total_eligible}")
        logger.info(f"Zero income households: {zero_income_households}")
        logger.info(f"Income eligible: {(household_df['income_eligible'].mean() * 100):.1f}%")
        logger.info(f"Food Stamps: {(household_df['food_stamps_receipent'].mean() * 100):.1f}%")
        logger.info(f"Public Assistance: {(household_df['public_assistance_receipent'].mean() * 100):.1f}%")

        # Filter and return eligible households
        eligible_households = household_df[household_df['eligible_calworks']].copy()
        return eligible_households

    except Exception as e:
        logger.error(f"Error calculating eligibility: {str(e)}")
        raise

def create_log_directory(config: dict, start_time: datetime) -> Path:
    """Create descriptive log directory with timestamp and key information."""
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    
    # Get PUMA range from default region
    region_def = config["regions"]["definitions"][config["regions"]["default"]]
    puma_codes = region_def["puma_codes"]
    puma_range = f"{min(puma_codes)}-{max(puma_codes)}"
    
    # Load initial data to get counts
    household_df = pd.read_csv(config["paths"]["household_data"])
    person_df = pd.read_csv(config["paths"]["person_data"])
    
    # Create descriptive folder name
    folder_name = (
        f"{timestamp}_"
        f"SF_PUMAs_{puma_range}_"
        f"HH{len(household_df)}_"
        f"P{len(person_df)}"
    )
    
    # Create log directory
    log_dir = Path("Script_python/after_main_run_logs") / folder_name
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create metadata file
    metadata = {
        "timestamp": timestamp,
        "puma_range": puma_range,
        "total_households": len(household_df),
        "total_persons": len(person_df),
        "mbsac_version": "2024_R1",
        "pipeline_version": config["pipeline"]["version"],
        "config_hash": hash(str(config))
    }
    
    with open(log_dir / "run_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
    
    return log_dir

def filter_region_data(
    household_df: pd.DataFrame,
    person_df: pd.DataFrame,
    region_name: str = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Filter data for specific region."""
    config = load_config()
    
    # Use default region if none specified
    if region_name is None:
        region_name = config["regions"]["default"]
    
    # Get region definition
    region_def = config["regions"]["definitions"][region_name]
    puma_codes = region_def["puma_codes"]
    
    # Filter households for region
    region_households = household_df[
        household_df["PUMA"].isin(puma_codes)
    ].copy()
    
    # Filter persons for region
    region_serialnos = set(region_households["SERIALNO"])
    region_persons = person_df[
        person_df["SERIALNO"].isin(region_serialnos)
    ].copy()
    
    logger.info(
        f"Filtered for {region_def['name']} - "
        f"Households: {len(region_households)}, "
        f"Persons: {len(region_persons)}"
    )
    
    return region_households, region_persons

def run_pipeline() -> int:
    """Execute the complete analysis pipeline."""
    try:
        # Load California data
        household_df, person_df = load_pums_data()
        
        # Calculate eligibility for all California
        eligible_households, eligible_persons = calculate_eligibility(
            household_df, person_df, config
        )
        
        # Save state-level results
        eligible_households.to_csv(config["paths"]["state_eligible_households"], index=False)
        eligible_persons.to_csv(config["paths"]["state_eligible_persons"], index=False)
        
        # Filter for specific region (San Francisco by default)
        region_households, region_persons = filter_region_data(
            eligible_households,
            eligible_persons
        )
        
        # Save region-specific results
        region_households.to_csv(config["paths"]["eligible_households"], index=False)
        region_persons.to_csv(config["paths"]["eligible_persons"], index=False)
        
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = run_pipeline()
    exit(exit_code)
