# Step 1: Preprocess PUMS Data
# Preproccessing.py is a script that reads in the PUMS data for households and persons, aggregates person-level data to the household level, and determines eligibility for CalWORKs based on the PUMS data. The script filters for households in San Francisco and saves the results to a CSV file.
# Location: Script_python/preprocessing.py
# CSV files: data/hca_2022.csv, data/pca_2022.csv
# Output: eligible_calworks_sf_households.csv
#
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from Script_python.utils.config import load_config, setup_logging
from Script_python.utils.data_ops import safe_numeric_conversion, validate_dataframe

# Setup logging and load config
logger = setup_logging()
config = load_config()


def load_pums_data(
    household_data_path: str, person_data_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load PUMS data for household and person records with error handling.

    Returns:
        tuple: (household_df, person_df)
    """
    try:
        # Load data
        household_df = pd.read_csv(household_data_path, low_memory=False)
        person_df = pd.read_csv(person_data_path, low_memory=False)

        # Debug: Print initial shapes
        logger.info(
            f"Initial data shapes - Households: {household_df.shape}, Persons: {person_df.shape}"
        )

        # Convert numeric columns first
        numeric_cols = ["HINCP", "NP", "PAP", "WAGP", "SEMP"]
        household_df = safe_numeric_conversion(household_df, ["HINCP", "NP"])
        person_df = safe_numeric_conversion(person_df, ["PAP", "WAGP", "SEMP"])

        # Remove invalid household sizes
        invalid_households = household_df[household_df["NP"] <= 0]
        if len(invalid_households) > 0:
            logger.warning(
                f"Removing {len(invalid_households)} households with invalid size (NP <= 0)"
            )
            household_df = household_df[household_df["NP"] > 0]

        # Fill NaN values with 0 for income-related columns
        person_df["PAP"] = person_df["PAP"].fillna(0)

        # Filter for San Francisco PUMA codes
        sf_puma_codes = config["puma"]["codes"]  # Updated to use new config structure
        household_df = household_df[
            (household_df["ST"] == 6) & (household_df["PUMA"].isin(sf_puma_codes))
        ].copy()  # Create a copy to avoid SettingWithCopyWarning

        # Filter persons based on household SERIALNO
        valid_serialnos = set(household_df["SERIALNO"])
        person_df = person_df[person_df["SERIALNO"].isin(valid_serialnos)].copy()

        # Debug: Print column presence
        logger.info(f"PAP column exists in person_df: {'PAP' in person_df.columns}")
        logger.info(f"PAP column values: {person_df['PAP'].value_counts().head()}")

        logger.info(
            f"Successfully loaded {len(household_df)} households and {len(person_df)} persons"
        )
        return household_df, person_df

    except Exception as e:
        logger.error(f"Error loading PUMS data: {str(e)}")
        raise


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

        aggregated_person_df = (
            person_df.groupby("SERIALNO")
            .agg({"PAP": ["sum", lambda x: (x > 0).any()]})
            .reset_index()
        )

        # Rename columns
        aggregated_person_df.columns = ["SERIALNO", "total_pap", "any_pap"]

        # Convert boolean to numeric
        aggregated_person_df["any_pap"] = aggregated_person_df["any_pap"].astype(int)

        return aggregated_person_df

    except Exception as e:
        logger.error(f"Error aggregating person data: {str(e)}")
        raise


def calculate_mbsac_threshold(household_size: int, config: dict) -> float:
    """Calculate MBSAC threshold for given household size."""
    # Handle invalid household sizes (0 or negative)
    if household_size <= 0:
        logger.warning(f"Invalid household size detected: {household_size}. Using threshold for size 1.")
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
            household_df['monthly_countable_income'] < household_df['MBSAC']
        )

        # Track eligibility reasons
        fs_col = config['categorical_eligibility']['food_stamps_col']
        pa_col = config['categorical_eligibility']['public_assistance_col']
        
        household_df['food_stamps_eligible'] = household_df[fs_col] == 1
        household_df['public_assistance_eligible'] = household_df[pa_col] > 0

        # Final eligibility determination
        household_df['eligible_calworks'] = (
            household_df['income_eligible'] |
            household_df['food_stamps_eligible'] |
            household_df['public_assistance_eligible']
        )

        # Calculate eligibility statistics
        total_eligible = len(household_df[household_df['eligible_calworks']])
        logger.info(f"Total eligible households: {total_eligible}")
        logger.info(f"Income eligible: {(household_df['income_eligible'].mean() * 100):.1f}%")
        logger.info(f"Food Stamps: {(household_df['food_stamps_eligible'].mean() * 100):.1f}%")
        logger.info(f"Public Assistance: {(household_df['public_assistance_eligible'].mean() * 100):.1f}%")

        # Filter and return eligible households
        eligible_households = household_df[household_df['eligible_calworks']].copy()
        return eligible_households

    except Exception as e:
        logger.error(f"Error calculating eligibility: {str(e)}")
        raise


if __name__ == "__main__":
    # Load PUMS data
    household_df, person_df = load_pums_data(
        config["paths"]["household_data"], config["paths"]["person_data"]
    )

    # Aggregate person data
    aggregated_person_df = aggregate_person_data(person_df)

    # Calculate eligibility
    eligible_households = calculate_eligibility(household_df, aggregated_person_df, config)

    # Save results to a CSV
    output_path = Path(config["paths"]["eligible_households"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    eligible_households.to_csv(output_path, index=False)
