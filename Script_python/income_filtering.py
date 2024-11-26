# Step 3: Calculate Income Metrics
# income_filtering.py: Calculate employment-based income and public assistance income for households based on the complete persons dataset.
# Location: Script_python/income_filtering.py
# CSV files: data/eligible_calworks_sf_households.csv, data/pca_2022.csv
# Output: filtered_income_metrics_households_with_full_persons.csv
#
from pathlib import Path

import pandas as pd
from Script_python.utils.config import Config, load_config


def calculate_income_metrics(config: Config) -> pd.DataFrame:
    """
    Calculate total employment-based and public assistance income for households
    based on the complete persons dataset.
    """
    # Load data
    households_path = config['paths']['eligible_households']
    all_persons_path = config['paths']['person_data']
    
    eligible_households = pd.read_csv(households_path)
    all_persons = pd.read_csv(all_persons_path)
    
    # Ensure income columns are numeric
    income_cols = ['WAGP', 'SEMP', 'PAP', 'RETP', 'INTP', 'SSP']
    all_persons[income_cols] = all_persons[income_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Calculate employment-based income and public assistance income
    all_persons['employment_income'] = all_persons['WAGP'] + all_persons['SEMP']
    all_persons['public_assistance_income'] = all_persons['PAP']
    
    # Aggregate income at the household level
    household_income_aggregates = all_persons.groupby('SERIALNO').agg(
        total_employment_income=('employment_income', 'sum'),
        total_public_assistance_income=('public_assistance_income', 'sum'),
        total_retirement_income=('RETP', 'sum'),
        total_dividend_income=('INTP', 'sum'),
        total_social_security_income=('SSP', 'sum')
    ).reset_index()
    
    # Merge with household data
    updated_households = pd.merge(
        eligible_households,
        household_income_aggregates,
        on='SERIALNO',
        how='left'
    )
    
    # Fill missing values for households with no income data
    income_columns = [
        'total_employment_income',
        'total_public_assistance_income',
        'total_retirement_income',
        'total_dividend_income',
        'total_social_security_income'
    ]
    updated_households[income_columns] = updated_households[income_columns].fillna(0)
    
    return updated_households
