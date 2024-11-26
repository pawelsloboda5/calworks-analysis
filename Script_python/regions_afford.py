# Step 4: Analyze Regions
# regions_afford.py: Analyze regions based on household income, rent, and income-to-rent ratio. The script groups households by region and calculates median values for key metrics. It then ranks regions based on these metrics to identify the top regions for further analysis.
# Location: Script_python/regions_afford.py
# CSV files: data/filtered_income_metrics_households_with_full_persons.csv, data/eligible_calworks_sf_persons.csv
# Output: region_analysis_with_all_income.csv, top_regions_for_analysis_with_all_income.csv
#
from pathlib import Path

import pandas as pd
from Script_python.utils.config import load_config


def analyze_regions(
    eligible_households: pd.DataFrame, eligible_persons: pd.DataFrame
) -> pd.DataFrame:
    """
    Analyze regions based on household income, rent, and income-to-rent ratio.
    """
    # Calculate monthly income
    eligible_households["monthly_income"] = eligible_households["HINCP"] / 12
    # Add flags for income sources
    eligible_households["has_employment_income"] = (
        eligible_households["total_employment_income"] > 0
    )
    eligible_households["has_public_assistance_income"] = (
        eligible_households["total_public_assistance_income"] > 0
    )
    eligible_households["has_retirement_income"] = (
        eligible_households["total_retirement_income"] > 0
    )
    eligible_households["has_dividend_income"] = (
        eligible_households["total_dividend_income"] > 0
    )
    eligible_households["has_social_security_income"] = (
        eligible_households["total_social_security_income"] > 0
    )

    # Aggregate households by region
    household_summary = (
        eligible_households.groupby("PUMA")
        .agg(
            total_households=("SERIALNO", "count"),
            median_rent=("GRNTP", "median"),
            median_income=("monthly_income", "median"),
            median_income_to_rent_ratio=(
                "monthly_income",
                lambda x: x.median()
                / eligible_households.loc[x.index, "GRNTP"].median(),
            ),
            median_employment_income=("total_employment_income", "median"),
            median_public_assistance_income=(
                "total_public_assistance_income",
                "median",
            ),
            median_retirement_income=("total_retirement_income", "median"),
            median_dividend_income=("total_dividend_income", "median"),
            median_social_security_income=("total_social_security_income", "median"),
            total_employment_income=("total_employment_income", "sum"),
            total_public_assistance_income=("total_public_assistance_income", "sum"),
            total_retirement_income=("total_retirement_income", "sum"),
            total_dividend_income=("total_dividend_income", "sum"),
            total_social_security_income=("total_social_security_income", "sum"),
            households_with_employment_income=("has_employment_income", "sum"),
            households_with_public_assistance_income=(
                "has_public_assistance_income",
                "sum",
            ),
            households_with_retirement_income=("has_retirement_income", "sum"),
            households_with_dividend_income=("has_dividend_income", "sum"),
            households_with_social_security_income=(
                "has_social_security_income",
                "sum",
            ),
        )
        .reset_index()
    )

    eligible_households["has_employment_income"] = (
        eligible_households["total_employment_income"] > 0
    )
    eligible_households["has_public_assistance_income"] = (
        eligible_households["total_public_assistance_income"] > 0
    )
    eligible_households["has_retirement_income"] = (
        eligible_households["total_retirement_income"] > 0
    )
    eligible_households["has_dividend_income"] = (
        eligible_households["total_dividend_income"] > 0
    )
    eligible_households["has_social_security_income"] = (
        eligible_households["total_social_security_income"] > 0
    )

    # Aggregate persons by region
    person_summary = (
        eligible_persons.groupby("PUMA")
        .agg(total_people=("SERIALNO", "count"))
        .reset_index()
    )

    # Merge summaries
    region_summary = pd.merge(household_summary, person_summary, on="PUMA", how="inner")
    region_summary["rent_stress"] = 1 / region_summary["median_income_to_rent_ratio"]

    # Round relevant columns
    numeric_columns = region_summary.select_dtypes(include=["float64"]).columns
    region_summary[numeric_columns] = region_summary[numeric_columns].round(2)

    return region_summary


if __name__ == "__main__":
    # Load configuration
    config = load_config()

    # Define paths
    data_dir = Path(config["paths"]["output_dir"])
    households_path = data_dir / "filtered_income_metrics_households.csv"
    persons_path = Path(config["paths"]["eligible_persons"])

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
