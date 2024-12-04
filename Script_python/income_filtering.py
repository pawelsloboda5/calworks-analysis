# Step 3: Calculate Income Metrics
# income_filtering.py: Calculate employment-based income and public assistance income for households based on the complete persons dataset.
# Location: Script_python/income_filtering.py
# CSV files: data/eligible_calworks_sf_households.csv, data/pca_2022.csv
# Output: filtered_income_metrics_households_with_full_persons.csv
#
from pathlib import Path

import pandas as pd
from Script_python.utils.config import Config, load_config
import numpy as np


def calculate_countable_income(person_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Calculate countable income according to CalWORKs rules."""
    """ Earned: WAGP (Wages/salary), SEMP (Self-employment)"""
    """ UNEARNED: RETP (Retirement), INTP (Interest), PAP (Public assistance)"""    
    
    # Create copy to avoid modifying original
    df = person_df.copy()
    
    # Initialize countable income columns
    df['earned_income'] = 0
    df['unearned_income'] = 0
    
    # Sum earned income sources
    for col in config['income']['income_columns']['earned']:
        df['earned_income'] += df[col].fillna(0)
    
    # Sum unearned income sources
    for col in config['income']['income_columns']['unearned']:
        df['unearned_income'] += df[col].fillna(0)
    
    # Apply earned income disregard
    df['earned_income_after_disregard'] = np.maximum(
        0, 
        df['earned_income'] - config['income']['earned_income_disregard']
    )
    
    # Calculate total countable income
    df['total_countable_income'] = (
        df['earned_income_after_disregard'] + 
        df['unearned_income']
    )
    
    return df

def calculate_income_metrics(config: dict) -> pd.DataFrame:
    """
    Calculate total employment-based and public assistance income for households
    based on the complete persons dataset.
    """
    # Load data
    households_path = config["paths"]["eligible_households"]
    all_persons_path = config["paths"]["person_data"]

    eligible_households = pd.read_csv(households_path)
    all_persons = pd.read_csv(all_persons_path)

    # Calculate countable income
    persons_with_income = calculate_countable_income(all_persons, config)
    
    # Aggregate income at household level
    household_income = (
        persons_with_income.groupby("SERIALNO")
        .agg(
            total_countable_income=("total_countable_income", "sum"),
            total_earned_income=("earned_income", "sum"),
            total_unearned_income=("unearned_income", "sum"),
            working_members=("earned_income", lambda x: (x > 0).sum())
        )
        .reset_index()
    )
    
    # Merge with household data
    updated_households = pd.merge(
        eligible_households,
        household_income,
        on="SERIALNO",
        how="left"
    )
    
    # Fill missing values
    income_columns = [
        "total_countable_income",
        "total_earned_income",
        "total_unearned_income",
        "working_members"
    ]
    updated_households[income_columns] = updated_households[income_columns].fillna(0)
    
    return updated_households
