"""Module for calculating employment and economic metrics."""
import pandas as pd

def calculate_employment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate employment-related metrics for each PUMA region."""
    df = df.copy()
    
    # Basic employment metrics
    df['unemployed_but_eligible'] = df['total_households'] - df['households_with_employment_income']
    df['employment_rate'] = (df['households_with_employment_income'] / df['total_households']) * 100
    
    # Economic impact metrics
    df['current_monthly_income'] = df['households_with_employment_income'] * df['median_income']
    df['potential_monthly_income'] = df['total_households'] * df['median_income']
    df['monthly_income_gap'] = df['potential_monthly_income'] - df['current_monthly_income']
    
    # Cost metrics
    avg_monthly_wage = df['median_income'].mean()
    df['estimated_program_cost'] = df['unemployed_but_eligible'] * (avg_monthly_wage * 0.5)  # 50% wage subsidy
    df['roi_ratio'] = df['monthly_income_gap'] / df['estimated_program_cost']
    
    return df 