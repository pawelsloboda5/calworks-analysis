# Script_python/main.py
"""
Main entry point for the CalWORKs Data Analysis pipeline.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime
from prettytable import PrettyTable
import json
import pandas as pd
from generate_visualizations import (
    plot_income_distribution,
    plot_eligibility_by_size,
    plot_eligibility_heatmap,
    generate_all_visualizations
)
from generate_plotly import generate_all_plotly_visualizations

from Script_python.preprocessing import (
    load_pums_data,
    create_log_directory,
    filter_region_data
)
from Script_python.utils.config import load_config, setup_logging
from Script_python.income_filtering import calculate_income_metrics
from Script_python.regions_afford import analyze_regions

logger = logging.getLogger(__name__)

def save_table_to_file(table: PrettyTable, log_dir: Path, filename: str) -> None:
    """Save PrettyTable to file."""
    with open(log_dir / filename, 'w') as f:
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(str(table))

def save_stats_to_json(stats: dict, log_dir: Path, filename: str) -> None:
    """Save statistics to JSON file."""
    with open(log_dir / filename, 'w') as f:
        json.dump(stats, f, indent=4)

def create_transformation_log(log_dir: Path) -> PrettyTable:
    """Create and initialize the data transformation tracking table."""
    transform_table = PrettyTable()
    transform_table.field_names = [
        "Step", 
        "Operation", 
        "Details", 
        "Input Size", 
        "Output Size", 
        "Change"
    ]
    transform_table.align = "l"
    return transform_table

def log_transformation(
    table: PrettyTable,
    step: str,
    operation: str,
    details: str,
    input_size: int,
    output_size: int
) -> None:
    """Add a transformation record to the tracking table."""
    change = output_size - input_size
    change_str = f"{change:+,d}" if change != 0 else "No change"
    table.add_row([
        step,
        operation,
        details,
        f"{input_size:,d}",
        f"{output_size:,d}",
        change_str
    ])

def save_data_loading_stats(household_df: pd.DataFrame, person_df: pd.DataFrame, log_dir: Path) -> None:
    """Save data loading statistics."""
    stats_table = PrettyTable()
    stats_table.field_names = ["Metric", "Value"]
    stats_table.add_row(["Total Households", f"{len(household_df):,}"])
    stats_table.add_row(["Total Persons", f"{len(person_df):,}"])
    stats_table.add_row(["Average Household Size", f"{len(person_df)/len(household_df):.2f}"])
    stats_table.add_row(["PUMA Regions", f"{household_df['PUMA'].nunique()}"])
    
    save_table_to_file(stats_table, log_dir, "01_data_loading_stats.txt")

def save_income_metrics(eligible_households: pd.DataFrame, log_dir: Path) -> None:
    """Save income-related statistics."""
    stats_table = PrettyTable()
    stats_table.field_names = ["Income Metric", "Value"]
    stats_table.add_row(["Median Monthly Income", f"${eligible_households['monthly_income'].median():,.2f}"])
    stats_table.add_row(["Mean Monthly Income", f"${eligible_households['monthly_income'].mean():,.2f}"])
    stats_table.add_row(["Working Households", f"{(eligible_households['working_members'] > 0).sum():,}"])
    stats_table.add_row(["Average Working Members", f"{eligible_households['working_members'].mean():.2f}"])
    
    save_table_to_file(stats_table, log_dir, "02_income_metrics.txt")

def save_eligibility_stats(eligible_households: pd.DataFrame, log_dir: Path) -> None:
    """Save eligibility statistics."""
    stats_table = PrettyTable()
    stats_table.field_names = ["Eligibility Metric", "Value"]
    
    # Total households
    total_hh = len(eligible_households)
    calworks_eligible = eligible_households["eligible_calworks"].sum()
    
    # Overall counts
    stats_table.add_row(["Total Households", f"{total_hh:,}"])
    stats_table.add_row(["CalWORKs Eligible", f"{calworks_eligible:,}"])
    stats_table.add_row(["CalWORKs Eligibility Rate", f"{(calworks_eligible/total_hh*100):.1f}%"])
    
    # Eligibility criteria breakdown
    stats_table.add_row(["", ""])  # Empty row for readability
    stats_table.add_row(["Eligibility Criteria Breakdown", ""])
    stats_table.add_row(["Income Eligible", f"{(eligible_households['income_eligible'].mean()*100):.1f}%"])
    stats_table.add_row(["Food Stamps Eligible", f"{(eligible_households['food_stamps_receipent'].mean()*100):.1f}%"])
    stats_table.add_row(["Public Assistance Eligible", f"{(eligible_households['public_assistance_receipent'].mean()*100):.1f}%"])
    
    save_table_to_file(stats_table, log_dir, "03_eligibility_stats.txt")

def save_column_tracking(initial_hh_cols: list, final_hh_cols: list, 
                        initial_person_cols: list, final_person_cols: list,
                        log_dir: Path) -> None:
    """Save column tracking information."""
    column_table = PrettyTable()
    column_table.field_names = ["Dataset", "Initial Columns", "Added Columns", "Final Columns"]
    
    # Get added columns
    added_hh_cols = sorted(set(final_hh_cols) - set(initial_hh_cols))
    added_person_cols = sorted(set(final_person_cols) - set(initial_person_cols))
    
    column_table.add_row([
        "Households",
        len(initial_hh_cols),
        ", ".join(added_hh_cols),
        len(final_hh_cols)
    ])
    column_table.add_row([
        "Persons",
        len(initial_person_cols),
        ", ".join(added_person_cols),
        len(final_person_cols)
    ])
    
    save_table_to_file(column_table, log_dir, "column_tracking.txt")

def save_detailed_statistics(
    household_df: pd.DataFrame,
    eligible_households: pd.DataFrame,
    region_households: pd.DataFrame,
    log_dir: Path
) -> None:
    """Generate detailed statistics report for visualization purposes."""
    stats_table = PrettyTable()
    stats_table.field_names = ["Category", "Metric", "State", "Region"]
    
    # Household Size Distribution
    stats_table.add_row(["", "", "", ""])  # Empty row for readability
    stats_table.add_row(["Household Size", "Distribution", "", ""])
    for size in range(1, 7):  # 1-6 person households
        state_pct = (eligible_households["NP"] == size).mean() * 100
        region_pct = (region_households["NP"] == size).mean() * 100
        stats_table.add_row(["", f"{size} Person", f"{state_pct:.1f}%", f"{region_pct:.1f}%"])
    stats_table.add_row(["", "7+ Person", 
        f"{(eligible_households['NP'] >= 7).mean()*100:.1f}%",
        f"{(region_households['NP'] >= 7).mean()*100:.1f}%"])

    # Income Brackets (Monthly)
    stats_table.add_row(["", "", "", ""])
    stats_table.add_row(["Income Brackets", "Distribution", "", ""])
    income_brackets = [
        (0, 1000, "Under $1,000"),
        (1000, 2500, "$1,000-$2,500"),
        (2500, 5000, "$2,500-$5,000"),
        (5000, 7500, "$5,000-$7,500"),
        (7500, 10000, "$7,500-$10,000"),
        (10000, float('inf'), "Over $10,000")
    ]
    for min_val, max_val, label in income_brackets:
        state_pct = ((eligible_households["monthly_income"] >= min_val) & 
                    (eligible_households["monthly_income"] < max_val)).mean() * 100
        region_pct = ((region_households["monthly_income"] >= min_val) & 
                     (region_households["monthly_income"] < max_val)).mean() * 100
        stats_table.add_row(["", label, f"{state_pct:.1f}%", f"{region_pct:.1f}%"])

    # Employment Statistics
    stats_table.add_row(["", "", "", ""])
    stats_table.add_row(["Employment", "By Working Members", "", ""])
    for workers in range(4):  # 0-3 workers
        state_pct = (eligible_households["working_members"] == workers).mean() * 100
        region_pct = (region_households["working_members"] == workers).mean() * 100
        label = "No Workers" if workers == 0 else f"{workers} Worker{'s' if workers > 1 else ''}"
        stats_table.add_row(["", label, f"{state_pct:.1f}%", f"{region_pct:.1f}%"])
    stats_table.add_row(["", "4+ Workers",
        f"{(eligible_households['working_members'] >= 4).mean()*100:.1f}%",
        f"{(region_households['working_members'] >= 4).mean()*100:.1f}%"])

    # CalWORKs Eligibility by Income Level
    stats_table.add_row(["", "", "", ""])
    stats_table.add_row(["CalWORKs Eligible", "By Income Bracket", "", ""])
    for min_val, max_val, label in income_brackets:
        state_mask = ((eligible_households["monthly_income"] >= min_val) & 
                     (eligible_households["monthly_income"] < max_val))
        region_mask = ((region_households["monthly_income"] >= min_val) & 
                      (region_households["monthly_income"] < max_val))
        
        state_pct = (eligible_households[state_mask]["eligible_calworks"].mean() * 100)
        region_pct = (region_households[region_mask]["eligible_calworks"].mean() * 100)
        stats_table.add_row(["", label, f"{state_pct:.1f}%", f"{region_pct:.1f}%"])

    save_table_to_file(stats_table, log_dir, "detailed_statistics.txt")

def get_income_ranges(households_df: pd.DataFrame, calworks_eligible_only: bool = False) -> dict:
    """Calculate detailed income ranges with proper monthly values."""
    if calworks_eligible_only:
        df = households_df[households_df['eligible_calworks']]
    else:
        df = households_df

    ranges = {
        "monthly": {
            "min": f"${df['monthly_income'].min():,.2f}",
            "max": f"${df['monthly_income'].max():,.2f}",
            "p25": f"${df['monthly_income'].quantile(0.25):,.2f}",
            "p50": f"${df['monthly_income'].quantile(0.50):,.2f}",
            "p75": f"${df['monthly_income'].quantile(0.75):,.2f}"
        },
        "household_size": {
            "min": int(df['NP'].min()),
            "max": int(df['NP'].max()),
            "avg": f"{df['NP'].mean():.1f}"
        }
    }
    
    # Add MBSAC thresholds if available
    if 'MBSAC' in df.columns:
        ranges["mbsac_thresholds"] = {
            "min": f"${df['MBSAC'].min():,.2f}",
            "max": f"${df['MBSAC'].max():,.2f}",
            "avg": f"${df['MBSAC'].mean():,.2f}"
        }
    else:
        ranges["mbsac_thresholds"] = {
            "min": "$0.00",
            "max": "$0.00",
            "avg": "$0.00"
        }
    
    return ranges

def calculate_detailed_statistics(region_households: pd.DataFrame, 
                                region_persons: pd.DataFrame,
                                eligible_households: pd.DataFrame) -> dict:
    """Calculate detailed statistics for final output."""
    
    # Calculate exact eligibility percentages
    total_households = len(region_households)
    eligibility_stats = {
        "income_eligible": (region_households['income_eligible'].sum() / total_households * 100),
        "food_stamps": (region_households['food_stamps_receipent'].sum() / total_households * 100),
        "receiving_public_assistance": (region_households['public_assistance_receipent'].sum() / total_households * 100)
    }
    
    # Get available income sources and their monthly values
    income_sources = {}
    income_columns = ['PAP', 'RETP', 'INTP', 'SSP']
    
    for col in income_columns:
        monthly_col = f'monthly_{col}'
        if monthly_col in region_households.columns:
            income_sources[col] = f"${region_households[monthly_col].mean():,.2f}"
        else:
            logger.warning(f"Monthly income column {monthly_col} not found in data")
            income_sources[col] = "$0.00"
    
    return {
        "total_persons": len(region_persons),
        "eligibility_breakdown": {
            "total_rate": f"{(total_households/total_households*100):.1f}%",
            "calworks_rate": f"{(region_households['eligible_calworks'].sum()/total_households*100):.1f}%",
            "income_eligible": f"{eligibility_stats['income_eligible']:.1f}%",
            "receiving_food_stamps": f"{eligibility_stats['food_stamps']:.1f}%",
            "receiving_public_assistance": f"{eligibility_stats['receiving_public_assistance']:.1f}%"
        },
        "income_ranges": {
            "calworks_eligible": {
                "monthly": {
                    "min": f"${region_households[region_households['eligible_calworks']]['monthly_income'].min():.2f}",
                    "max": f"${region_households[region_households['eligible_calworks']]['monthly_income'].max():.2f}",
                    "mean": f"${region_households[region_households['eligible_calworks']]['monthly_income'].mean():.2f}",
                    "p25": f"${region_households[region_households['eligible_calworks']]['monthly_income'].quantile(0.25):.2f}",
                    "p50": f"${region_households[region_households['eligible_calworks']]['monthly_income'].quantile(0.50):.2f}",
                    "p75": f"${region_households[region_households['eligible_calworks']]['monthly_income'].quantile(0.75):.2f}"
                }
            }
        },
        "income_sources": {
            "Public Assistance": income_sources['PAP'],
            "Retirement": income_sources['RETP'],
            "Interest": income_sources['INTP'],
            "Social Security": income_sources['SSP']
        }
    }

def calculate_state_statistics(household_df: pd.DataFrame, 
                             person_df: pd.DataFrame,
                             eligible_households: pd.DataFrame) -> dict:
    """Calculate detailed statistics for state-level summary."""
    
    total_households = len(household_df)
    calworks_eligible_mask = eligible_households['eligible_calworks']
    
    # Calculate income sources for state level
    available_income_cols = {
        'PAP': 'Public Assistance',
        'RETP': 'Retirement',
        'INTP': 'Interest',
        'SSP': 'Social Security'
    }
    
    income_sources = {}
    for col, label in available_income_cols.items():
        if col in person_df.columns:
            monthly_avg = person_df[col].sum() / (12 * total_households)
            income_sources[label] = f"${monthly_avg:,.2f}"
        else:
            income_sources[label] = "$0.00"
    
    # Calculate average monthly benefits for those receiving assistance
    avg_benefits = {
        "public_assistance": "$0.00",
        "food_stamps": "$0.00",
        "social_security": "$0.00"
    }
    
    # Calculate public assistance benefits if data available
    if 'PAP' in eligible_households.columns and 'public_assistance_receipent' in eligible_households.columns:
        pa_recipients = eligible_households[eligible_households['public_assistance_receipent'] == True]
        if len(pa_recipients) > 0:
            avg_benefits['public_assistance'] = f"${(pa_recipients['PAP'].mean() / 12):,.2f}"
    
    # Calculate social security benefits if available
    if 'SSP' in eligible_households.columns:
        ss_recipients = eligible_households[eligible_households['SSP'] > 0]
        if len(ss_recipients) > 0:
            avg_benefits['social_security'] = f"${(ss_recipients['SSP'].mean() / 12):,.2f}"
    
    return {
        "total_households": int(total_households),
        "total_persons": len(person_df),
        "eligible_households": int(len(eligible_households)),
        "calworks_eligible": int(eligible_households["eligible_calworks"].sum()),
        "eligibility_breakdown": {
            "total_rate": f"{(len(eligible_households)/total_households*100):.1f}%",
            "calworks_rate": f"{(eligible_households['eligible_calworks'].sum()/len(eligible_households)*100):.1f}%",
            "income_eligible": f"{(eligible_households['income_eligible'].mean()*100):.1f}%",
            "receiving_food_stamps": f"{(eligible_households['food_stamps_receipent'].mean()*100):.1f}%",
            "receiving_public_assistance": f"{(eligible_households['public_assistance_receipent'].mean()*100):.1f}%"
        },
        "income_metrics": {
            "median_monthly": f"${eligible_households['monthly_income'].median():,.2f}",
            "mean_monthly": f"${eligible_households['monthly_income'].mean():,.2f}",
            "working_households": int((eligible_households['working_members'] > 0).sum()),
            "avg_working_members": f"{eligible_households['working_members'].mean():.2f}",
            "income_sources": income_sources
        },
        "income_ranges": {
            "all_households": get_income_ranges(household_df),
            "calworks_eligible": get_income_ranges(eligible_households, calworks_eligible_only=True)
        },
        "income_distribution": {
            "below_1000": f"{(household_df['monthly_income'] < 1000).mean()*100:.1f}%",
            "1000_2500": f"{((household_df['monthly_income'] >= 1000) & (household_df['monthly_income'] < 2500)).mean()*100:.1f}%",
            "2500_5000": f"{((household_df['monthly_income'] >= 2500) & (household_df['monthly_income'] < 5000)).mean()*100:.1f}%",
            "5000_plus": f"{(household_df['monthly_income'] >= 5000).mean()*100:.1f}%"
        },
        "demographics": {
            "avg_household_size": f"{len(person_df)/total_households:.2f}",
            "household_size_distribution": {
                "1_person": f"{(household_df['NP'] == 1).mean()*100:.1f}%",
                "2_person": f"{(household_df['NP'] == 2).mean()*100:.1f}%",
                "3_4_person": f"{((household_df['NP'] >= 3) & (household_df['NP'] <= 4)).mean()*100:.1f}%",
                "5_plus": f"{(household_df['NP'] >= 5).mean()*100:.1f}%"
            }
        },
        "assistance_status": {
            "current_recipients": {
                "food_stamps": f"{(eligible_households['food_stamps_receipent'].sum()):,}",
                "public_assistance": f"{(eligible_households['public_assistance_receipent'].sum()):,}"
            },
            "average_monthly_benefits": avg_benefits
        }
    }

def run_pipeline() -> int:
    """Execute the complete analysis pipeline."""
    start_time = datetime.now()
    
    try:
        # Initialize logging and configuration
        logger = setup_logging()
        config = load_config()
        
        # Create log directory with descriptive name
        log_dir = create_log_directory(config, start_time)
        logger.info(f"Created log directory: {log_dir}")

        # Initialize transformation tracking
        transform_table = create_transformation_log(log_dir)

        # Step 1: Load Data
        household_df, person_df = load_pums_data()
        initial_hh_cols = household_df.columns.tolist()
        initial_person_cols = person_df.columns.tolist()
        save_data_loading_stats(household_df, person_df, log_dir)

        # Step 2: Calculate Income Metrics
        eligible_households, persons_with_income = calculate_income_metrics(
            household_df, person_df
        )
        save_income_metrics(eligible_households, log_dir)

        # Step 3: Filter Region and Calculate Eligibility
        region_households, region_persons = filter_region_data(
            eligible_households,
            persons_with_income
        )
        save_eligibility_stats(region_households, log_dir)

        # Save column tracking at the end
        save_column_tracking(
            initial_hh_cols, region_households.columns.tolist(),
            initial_person_cols, region_persons.columns.tolist(),
            log_dir
        )

        # Step 4: Regional Analysis
        step4_start = datetime.now()
        logger.info("Step 4: Analyzing regional data...")
        region_summary = analyze_regions(region_households, region_persons)

        # Create regional statistics table
        region_table = PrettyTable()
        region_table.field_names = ["PUMA", "Total HH", "Eligible HH", "Eligibility Rate", "Median Income"]
        for puma in sorted(region_summary['PUMA'].unique()):
            puma_data = region_summary[region_summary['PUMA'] == puma].iloc[0]
            region_table.add_row([
                puma,
                puma_data['total_households'],
                puma_data['households_count'],
                f"{(puma_data['households_count']/puma_data['total_households']*100):.1f}%",
                f"${puma_data['median_income']:,.2f}"
            ])
        save_table_to_file(region_table, log_dir, "04_regional_analysis.txt")

        # Step 5: Generate Visualizations
        step5_start = datetime.now()

        # Create visualization directory in log folder
        viz_dir = log_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Step 5: Generating visualizations...")
        # Generate matplotlib visualizations
        generate_all_visualizations(region_households, viz_dir)
        
        # Generate interactive Plotly visualizations
        logger.info("Generating interactive Plotly visualizations...")
        generate_all_plotly_visualizations(region_households, viz_dir)

        # Save transformation log and final statistics
        save_table_to_file(transform_table, log_dir, "data_transformation_log.txt")
        
        # Get region info for final stats
        region_name = config["regions"]["default"]
        region_def = config["regions"]["definitions"][region_name]
        
        # Calculate detailed statistics
        detailed_stats = calculate_detailed_statistics(
            region_households, 
            region_persons,
            eligible_households
        )
        
        # Update final statistics with detailed stats
        final_stats = {
            "execution_time": str(datetime.now() - start_time),
            "state_summary": calculate_state_statistics(household_df, person_df, eligible_households),
            "region_summary": {
                "name": region_def["name"],
                "total_households": int(len(region_households)),
                "total_persons": detailed_stats["total_persons"],
                "calworks_eligible": int(region_households["eligible_calworks"].sum()),
                "eligibility_breakdown": detailed_stats["eligibility_breakdown"],
                "income_metrics": {
                    "median_monthly": f"${region_households['monthly_income'].median():,.2f}",
                    "mean_monthly": f"${region_households['monthly_income'].mean():,.2f}",
                    "working_households": int((region_households['working_members'] > 0).sum()),
                    "avg_working_members": f"{region_households['working_members'].mean():.2f}",
                    "income_sources": detailed_stats["income_sources"]
                },
                "income_ranges": {
                    "all_households": get_income_ranges(region_households),
                    "calworks_eligible": {
                        **get_income_ranges(region_households, calworks_eligible_only=True),
                        "monthly": detailed_stats["income_ranges"]["calworks_eligible"]["monthly"]
                    }
                },
                "income_distribution": {
                    "below_1000": f"{(region_households['monthly_income'] < 1000).mean()*100:.1f}%",
                    "1000_2500": f"{((region_households['monthly_income'] >= 1000) & (region_households['monthly_income'] < 2500)).mean()*100:.1f}%",
                    "2500_5000": f"{((region_households['monthly_income'] >= 2500) & (region_households['monthly_income'] < 5000)).mean()*100:.1f}%",
                    "5000_plus": f"{(region_households['monthly_income'] >= 5000).mean()*100:.1f}%"
                },
                "demographics": {
                    "avg_household_size": f"{len(region_persons)/len(region_households):.2f}",
                    "household_size_distribution": {
                        "1_person": f"{(region_households['NP'] == 1).mean()*100:.1f}%",
                        "2_person": f"{(region_households['NP'] == 2).mean()*100:.1f}%",
                        "3_4_person": f"{((region_households['NP'] >= 3) & (region_households['NP'] <= 4)).mean()*100:.1f}%",
                        "5_plus": f"{(region_households['NP'] >= 5).mean()*100:.1f}%"
                    }
                }
            },
            "comparison_metrics": {
                "eligibility_rate_difference": f"{(region_households['eligible_calworks'].mean() - eligible_households['eligible_calworks'].mean())*100:.1f}%",
                "median_income_ratio": f"{region_households['monthly_income'].median() / eligible_households['monthly_income'].median():.2f}",
                "working_households_difference": f"{(region_households['working_members'] > 0).mean() - (eligible_households['working_members'] > 0).mean():.1f}%"
            }
        }
        
        # Save final statistics
        save_stats_to_json(final_stats, log_dir, "final_statistics.json")

        # Generate detailed statistics
        save_detailed_statistics(
            household_df,
            eligible_households,
            region_households,
            log_dir
        )

        logger.info(f"Pipeline completed successfully in {datetime.now() - start_time}")
        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_pipeline())
