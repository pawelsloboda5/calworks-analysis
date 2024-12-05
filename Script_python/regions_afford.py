# Step 4: Analyze Regions
# Script_python/regions_afford.py: Analyze regions based on household income, rent, and income-to-rent ratio.
from pathlib import Path
from Script_python.utils.config import load_config
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def safe_median_ratio(income_series, rent_series) -> float:
    """Calculate median income to rent ratio, handling zero rent values."""
    try:
        median_income = income_series.median()
        median_rent = rent_series.median()
        
        if pd.isna(median_rent) or median_rent == 0:
            logger.warning(f"Zero or NaN median rent found for PUMA {income_series.name}")
            return 0.0
        
        if pd.isna(median_income):
            logger.warning(f"NaN median income found for PUMA {income_series.name}")
            return 0.0
            
        return median_income / median_rent
    except Exception as e:
        logger.error(f"Error calculating median ratio: {str(e)}")
        return 0.0

def analyze_regions(
    eligible_households: pd.DataFrame, eligible_persons: pd.DataFrame
) -> pd.DataFrame:
    """
    Analyze regions based on household income, rent, and income-to-rent ratio.
    Note: All income values from PUMS are 12-month totals.
    """
    logger.info("Starting regional analysis...")

    # First filter persons to match eligible households
    eligible_serialnos = set(eligible_households["SERIALNO"])
    eligible_persons = eligible_persons[
        eligible_persons["SERIALNO"].isin(eligible_serialnos)
    ].copy()

    # Ensure monthly income columns exist
    if 'monthly_income' not in eligible_households.columns and 'HINCP' in eligible_households.columns:
        eligible_households["monthly_income"] = eligible_households["HINCP"] / 12
    
    # Add flags for employment income
    if "total_earned_income" in eligible_households.columns:
        eligible_households["monthly_earned_income"] = eligible_households["total_earned_income"] / 12
        eligible_households["has_employment_income"] = eligible_households["total_earned_income"] > 0
    else:
        logger.warning("total_earned_income not found, setting has_employment_income to False")
        eligible_households["has_employment_income"] = False
        eligible_households["monthly_earned_income"] = 0
    
    # Define income columns we want to analyze
    person_income_cols = ["RETP", "INTP", "PAP", "SSP"]
    
    # Create monthly versions of income columns if they don't exist
    for col in person_income_cols:
        monthly_col = f'monthly_{col}'
        if col in eligible_persons.columns and monthly_col not in eligible_persons.columns:
            eligible_persons[monthly_col] = eligible_persons[col] / 12
            logger.info(f"Created {monthly_col} from {col}")
        elif col not in eligible_persons.columns:
            logger.warning(f"Column {col} not found in person data, adding with zeros")
            eligible_persons[col] = 0
            eligible_persons[monthly_col] = 0
    
    # First, aggregate person-level income data to household level (using monthly values)
    monthly_cols = [f'monthly_{col}' for col in person_income_cols]
    person_income_agg = (
        eligible_persons.groupby("SERIALNO")[monthly_cols]
        .sum()
        .reset_index()
    )
    
    # Merge person income data with household data
    eligible_households = pd.merge(
        eligible_households,
        person_income_agg,
        on="SERIALNO",
        how="left",
        suffixes=('', '_person')
    )
    
    # Fill NaN values with 0 for the income columns
    for col in monthly_cols:
        if col in eligible_households.columns:
            eligible_households[col] = eligible_households[col].fillna(0)
        else:
            logger.warning(f"Column {col} not found after merge, adding with zeros")
            eligible_households[col] = 0
    
    # Add flags for other income sources (using monthly values for comparison)
    eligible_households["has_public_assistance_income"] = eligible_households["monthly_PAP"] > 0
    eligible_households["has_retirement_income"] = eligible_households["monthly_RETP"] > 0
    eligible_households["has_dividend_income"] = eligible_households["monthly_INTP"] > 0
    eligible_households["has_social_security_income"] = eligible_households["monthly_SSP"] > 0

    # Get total households by PUMA for calculating percentages
    total_households_by_puma = eligible_households.groupby("PUMA").size().reset_index(name='total_households')

    # Build aggregation dictionary based on available columns
    agg_dict = {
        "SERIALNO": "count",  # This becomes households_count
        "GRNTP": "median",    # This becomes median_rent
        "monthly_income": "median"  # This becomes median_income
    }
    
    # Add income-related columns if they exist
    if "monthly_earned_income" in eligible_households.columns:
        agg_dict["monthly_earned_income"] = "median"
    
    for col in monthly_cols:
        if col in eligible_households.columns:
            agg_dict[col] = "median"
    
    if "total_earned_income" in eligible_households.columns:
        agg_dict["total_earned_income"] = "sum"
    
    for col in person_income_cols:
        if col in eligible_households.columns:
            agg_dict[col] = "sum"
    
    # Add flag columns if they exist
    flag_cols = [
        "has_employment_income",
        "has_public_assistance_income",
        "has_retirement_income",
        "has_dividend_income",
        "has_social_security_income"
    ]
    
    for col in flag_cols:
        if col in eligible_households.columns:
            agg_dict[col] = "sum"

    # Aggregate households by region using available columns
    household_summary = (
        eligible_households.groupby("PUMA")
        .agg(**{
            "households_count": ("SERIALNO", "count"),
            "median_rent": ("GRNTP", "median"),
            "median_income": ("monthly_income", "median"),
            "median_income_to_rent_ratio": (
                "monthly_income",
                lambda x: safe_median_ratio(x, eligible_households.loc[x.index, "GRNTP"])
            ),
            **{k: (k, v) for k, v in agg_dict.items() if k in eligible_households.columns}
        })
        .reset_index()
    )

    # Merge with total households
    region_summary = pd.merge(household_summary, total_households_by_puma, on="PUMA")
    
    # Round relevant columns
    numeric_columns = region_summary.select_dtypes(include=["float64"]).columns
    region_summary[numeric_columns] = region_summary[numeric_columns].round(2)

    return region_summary


if __name__ == "__main__":
    # Load configuration from YAML
    config = load_config()

    # Define paths
    data_dir = config["paths"]["output_dir"]
    households_path = data_dir / "filtered_income_metrics_households.csv"
    persons_path = config["paths"]["eligible_persons"]

    # Load data
    eligible_households = pd.read_csv(households_path)
    eligible_persons = pd.read_csv(persons_path)

    # Analyze regions
    region_summary = analyze_regions(eligible_households, eligible_persons)

    # Save outputs
    output_path = data_dir / "region_analysis.csv"
    region_summary.to_csv(output_path, index=False)

    # Save top regions
    top_regions = region_summary.head(3)
    top_regions.to_csv(data_dir / "top_regions_for_analysis.csv", index=False)

    print("\nTop 3 Regions for Further Analysis (Median-based):")
    print(top_regions)
