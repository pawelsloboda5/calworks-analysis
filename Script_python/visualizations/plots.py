"""
Visualization module for generating standard plots and charts.
"""

import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from Script_python.utils.config import setup_logging
from typing import Union

logger = setup_logging()


def setup_plot_style() -> None:
    """Configure default plot styling."""
    sns.set_theme(style="whitegrid")
    sns.set_palette("husl")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12


def plot_income_distribution(df: pd.DataFrame, output_dir: Union[str, Path]) -> None:
    """Generate income distribution plots."""
    setup_plot_style()
    plt.figure()
    df["PUMA"] = df["PUMA"].astype(str)
    ax = sns.boxplot(x="PUMA", y="median_income", data=df)
    plt.title("Monthly Income Distribution by PUMA Region")
    plt.xlabel("PUMA Region")
    plt.ylabel("Monthly Income ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "income_distribution.png", dpi=300)
    plt.close()
    logger.info("Generated income distribution plot.")


def plot_income_sources(df: pd.DataFrame, output_dir: Union[str, Path]) -> None:
    """Generate income sources comparison plot."""
    setup_plot_style()
    income_sources = [
        "median_employment_income",
        "median_public_assistance_income",
        "median_retirement_income",
        "median_dividend_income",
        "median_social_security_income",
    ]
    source_labels = {
        "median_employment_income": "Employment",
        "median_public_assistance_income": "Public Assistance",
        "median_retirement_income": "Retirement",
        "median_dividend_income": "Dividends",
        "median_social_security_income": "Social Security",
    }
    plt.figure(figsize=(14, 7))
    df["PUMA"] = df["PUMA"].astype(str)
    df_melted = df.melt(
        id_vars=["PUMA"],
        value_vars=income_sources,
        var_name="Income Source",
        value_name="Amount",
    )
    df_melted["Income Source"] = df_melted["Income Source"].map(source_labels)
    ax = sns.barplot(x="PUMA", y="Amount", hue="Income Source", data=df_melted)
    plt.title("Income Sources by PUMA Region")
    plt.xlabel("PUMA Region")
    plt.ylabel("Amount ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.xticks(rotation=45)
    plt.legend(title="Income Source", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "income_sources.png", bbox_inches="tight", dpi=300)
    plt.close()
    logger.info("Generated income sources plot.")


def plot_rent_burden(df: pd.DataFrame, output_dir: Union[str, Path]) -> None:
    """Generate rent burden analysis plots."""
    setup_plot_style()
    plt.figure()
    df["PUMA"] = df["PUMA"].astype(str)
    ax = sns.barplot(x="PUMA", y="rent_stress", data=df)
    plt.title("Rent Burden by PUMA Region")
    plt.xlabel("PUMA Region")
    plt.ylabel("Rent-to-Income Ratio")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1%}"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "rent_burden.png", dpi=300)
    plt.close()
    logger.info("Generated rent burden plot.")


def plot_household_stats(df: pd.DataFrame, output_dir: Union[str, Path]) -> None:
    """Generate household statistics plots."""
    setup_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    df["PUMA"] = df["PUMA"].astype(str)
    sns.barplot(x="PUMA", y="total_households", data=df, ax=ax1)
    ax1.set_title("Total Households by PUMA Region")
    ax1.set_xlabel("PUMA Region")
    ax1.set_ylabel("Number of Households")
    ax1.tick_params(axis="x", rotation=45)
    for container in ax1.containers:
        ax1.bar_label(container, padding=3)
    sns.barplot(x="PUMA", y="total_people", data=df, ax=ax2)
    ax2.set_title("Total People by PUMA Region")
    ax2.set_xlabel("PUMA Region")
    ax2.set_ylabel("Number of People")
    ax2.tick_params(axis="x", rotation=45)
    for container in ax2.containers:
        ax2.bar_label(container, padding=3)
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "household_stats.png", dpi=300)
    plt.close()
    logger.info("Generated household statistics plot.")


def plot_income_analysis(df: pd.DataFrame, output_dir: Union[str, Path]) -> None:
    """Generate detailed income analysis plots."""
    setup_plot_style()
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3)

    # 1. Employment Rate Plot
    ax1 = fig.add_subplot(gs[0, 0])
    df["employment_rate"] = (
        df["households_with_employment_income"] / df["total_households"]
    ) * 100
    sns.barplot(x="PUMA", y="employment_rate", data=df, ax=ax1)
    ax1.set_title("Employment Rate by PUMA Region")
    ax1.set_xlabel("PUMA Region")
    ax1.set_ylabel("% of Households with Employment Income")
    ax1.tick_params(axis="x", rotation=45)
    for container in ax1.containers:
        ax1.bar_label(container, fmt="%.1f%%", padding=3)
    ax1.set_ylim(0, 100)

    # 2. Income Source Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    source_columns = [
        "households_with_employment_income",
        "households_with_public_assistance_income",
        "households_with_retirement_income",
        "households_with_dividend_income",
        "households_with_social_security_income",
    ]
    source_labels = {
        "households_with_employment_income": "Employment",
        "households_with_public_assistance_income": "Public Assistance",
        "households_with_retirement_income": "Retirement",
        "households_with_dividend_income": "Dividends",
        "households_with_social_security_income": "Social Security",
    }
    for col in source_columns:
        df[col + "_percent"] = (df[col] / df["total_households"]) * 100
    df_melted = df.melt(
        id_vars=["PUMA"],
        value_vars=[col + "_percent" for col in source_columns],
        var_name="Income Source",
        value_name="Percentage",
    )
    df_melted["Income Source"] = df_melted["Income Source"].map(
        lambda x: source_labels[x.replace("_percent", "")]
    )
    sns.barplot(x="PUMA", y="Percentage", hue="Income Source", data=df_melted, ax=ax2)
    ax2.set_title("Income Source Distribution")
    ax2.set_xlabel("PUMA Region")
    ax2.set_ylabel("Percentage of Households")
    ax2.tick_params(axis="x", rotation=45)
    ax2.legend(title="Income Source", bbox_to_anchor=(1.05, 1), loc="upper left")

    # 3. Mean vs Median Income
    ax3 = fig.add_subplot(gs[1, 0])
    income_stats = pd.DataFrame(
        {
            "PUMA": df["PUMA"].astype(str),
            "Median Income": df["median_income"],
            "Mean Income": df["total_employment_income"] / df["total_households"],
        }
    )
    income_stats_melted = income_stats.melt(
        id_vars=["PUMA"], var_name="Statistic", value_name="Income"
    )
    sns.barplot(x="PUMA", y="Income", hue="Statistic", data=income_stats_melted, ax=ax3)
    ax3.set_title("Mean vs Median Monthly Income")
    ax3.set_xlabel("PUMA Region")
    ax3.set_ylabel("Income ($)")
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax3.tick_params(axis="x", rotation=45)
    ax3.legend(title="Statistic", bbox_to_anchor=(1.05, 1), loc="upper left")

    # 4. Income Source Presence
    ax4 = fig.add_subplot(gs[1, 1])
    source_presence = pd.DataFrame(
        {
            "PUMA": df["PUMA"].astype(str),
            "Employment": df["households_with_employment_income"]
            / df["total_households"]
            * 100,
            "Public Assistance": df["households_with_public_assistance_income"]
            / df["total_households"]
            * 100,
            "Retirement": df["households_with_retirement_income"]
            / df["total_households"]
            * 100,
            "Dividends": df["households_with_dividend_income"]
            / df["total_households"]
            * 100,
            "Social Security": df["households_with_social_security_income"]
            / df["total_households"]
            * 100,
        }
    )
    source_presence_melted = source_presence.melt(
        id_vars=["PUMA"], var_name="Income Source", value_name="Percentage"
    )
    sns.barplot(
        x="PUMA",
        y="Percentage",
        hue="Income Source",
        data=source_presence_melted,
        ax=ax4,
    )
    ax4.set_title("Presence of Income Sources")
    ax4.set_xlabel("PUMA Region")
    ax4.set_ylabel("% of Households")
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1f}%"))
    ax4.tick_params(axis="x", rotation=45)
    ax4.legend(title="Income Source", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(Path(output_dir) / "income_analysis.png", bbox_inches="tight", dpi=300)
    plt.close()
    logger.info("Generated income analysis plots.")


def generate_summary_plots(
    region_summary: pd.DataFrame, output_dir: Union[str, Path]
) -> None:
    """Generate all summary plots."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_income_distribution(region_summary, output_dir)
    plot_income_sources(region_summary, output_dir)
    plot_rent_burden(region_summary, output_dir)
    plot_household_stats(region_summary, output_dir)
    plot_income_analysis(region_summary, output_dir)
    logger.info("All plots generated successfully.")
