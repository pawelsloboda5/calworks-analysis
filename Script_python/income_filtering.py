# Step 2: Calculate Income Metrics
# Location: Script_python/income_filtering.py

from pathlib import Path
from Script_python.utils.config import load_config, setup_logging

import pandas as pd
from Script_python.utils.config import Config, load_config
import numpy as np
import logging
from typing import Tuple

# Setup logging
logger = logging.getLogger(__name__)

def calculate_countable_income(person_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Calculate countable income according to CalWORKs rules.
    All input income values (WAGP, SEMP, RETP, INTP, PAP, SSP) are 12-month totals.
    Returns both annual and monthly income values."""

    # Create copy to avoid modifying original
    df = person_df.copy()
    
    # Initialize countable income columns (annual values)
    df['earned_income'] = 0
    df['unearned_income'] = 0
    
    # Sum earned income sources (annual values)
    if 'WAGP' in df.columns and 'SEMP' in df.columns:
        df['earned_income'] = df['WAGP'].fillna(0) + df['SEMP'].fillna(0)
    
    # Sum unearned income sources (annual values)
    unearned_cols = ['RETP', 'INTP', 'PAP', 'SSP']
    for col in unearned_cols:
        if col in df.columns:
            df['unearned_income'] += df[col].fillna(0)
    
    # Calculate total countable income
    df['total_countable_income'] = df['earned_income'] + df['unearned_income']
    df['total_earned_income'] = df['earned_income']
    df['total_unearned_income'] = df['unearned_income']
    
    # Add working flag
    df['working_members'] = (df['earned_income'] > 0).astype(int)
    
    return df

def calculate_household_PAP_income(
    household_df: pd.DataFrame,
    person_df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate household-level public assistance income from person-level data."""
    # Aggregate PAP at household level
    household_pap = (
        person_df.groupby("SERIALNO")
        .agg(
            PAP=("PAP", "sum"),
            any_pap=("PAP", lambda x: (x > 0).any())
        )
        .reset_index()
    )
    
    # Merge with household data
    household_df = pd.merge(
        household_df,
        household_pap,
        on="SERIALNO",
        how="left"
    ).fillna(0)
    
    return household_df

def calculate_income_metrics(
    household_df: pd.DataFrame,
    person_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate income metrics and eligibility for households."""
    config = load_config()
    
    initial_count = len(household_df)
    logger.info(f"Initial households before income calculation: {initial_count}")
    
    # Calculate countable income
    persons_with_income = calculate_countable_income(person_df, config)
    
    # Aggregate monthly income columns at household level
    monthly_cols = ['monthly_PAP', 'monthly_RETP', 'monthly_INTP', 'monthly_SSP']
    income_agg = {}
    
    for col in monthly_cols:
        if col in persons_with_income.columns:
            income_agg[col] = 'sum'
    
    # Add PAP income and other metrics at household level
    household_income = (
        persons_with_income.groupby("SERIALNO")
        .agg({
            "total_countable_income": "sum",
            "total_earned_income": "sum",
            "total_unearned_income": "sum",
            "working_members": "sum",
            "PAP": "sum",  # Add PAP aggregation
            **income_agg  # Include monthly columns in aggregation
        })
        .reset_index()
    )
    
    # Merge with household data
    eligible_households = pd.merge(
        household_df,
        household_income,
        on="SERIALNO",
        how="left"
    ).fillna(0)
    
    # Ensure monthly_income exists
    if 'monthly_income' not in eligible_households.columns:
        eligible_households["monthly_income"] = eligible_households["HINCP"] / 12
    
    # Calculate MBSAC thresholds
    eligible_households["MBSAC"] = eligible_households["NP"].apply(
        lambda x: calculate_mbsac_threshold(x, config)
    )
    
    # Determine eligibility
    eligible_households["income_eligible"] = (
        eligible_households["monthly_income"] <= eligible_households["MBSAC"]
    )
    eligible_households["food_stamps_receipent"] = eligible_households["FS"] == 1
    eligible_households["public_assistance_receipent"] = eligible_households["PAP"] > 0
    
    # Overall CalWORKs eligibility
    eligible_households["eligible_calworks"] = (
        (eligible_households["income_eligible"] |
         eligible_households["food_stamps_receipent"] |
         eligible_households["public_assistance_receipent"]) &
        (eligible_households["monthly_income"] > -1) &
        (eligible_households["NP"] > 0) &
        (eligible_households["MBSAC"] > 0)
    )
    
    logger.info(f"Households after income merge: {len(eligible_households)}")
    logger.info(f"CalWORKs eligible households: {eligible_households['eligible_calworks'].sum()}")
    
    return eligible_households, persons_with_income

def calculate_mbsac_threshold(household_size: int, config: dict) -> float:
    """Calculate MBSAC threshold for a given household size."""
    if household_size <= 0:
        return config['mbsac_thresholds'][1]
    
    if household_size <= 10:
        return config['mbsac_thresholds'][household_size]
    else:
        base_amount = config['mbsac_thresholds'][10]
        extra_persons = household_size - 10
        return base_amount + (extra_persons * config['mbsac_thresholds']['additional_person'])
