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
import numpy as np

logger = setup_logging()


def setup_plot_style() -> None:
    """Configure consistent plot styling."""
    plt.style.use('seaborn')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['figure.dpi'] = 300


def plot_eligibility_breakdown(df: pd.DataFrame, output_dir: Path) -> None:
    """Create eligibility criteria distribution plot."""
    setup_plot_style()
    
    # Calculate percentages
    stats = {
        'Income Eligible': (df['income_eligible'].mean() * 100),
        'Receives Food Stamps': (df['food_stamps_eligible'].mean() * 100),
        'Receives Public Assistance': (df['public_assistance_eligible'].mean() * 100)
    }
    
    # Create bar plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(stats.keys(), stats.values())
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    plt.title('CalWORKs Eligibility Criteria Distribution')
    plt.ylabel('Percentage of Households (%)')
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(output_dir / 'eligibility_breakdown.png', bbox_inches='tight')
    plt.close()


def plot_income_distribution(df: pd.DataFrame, output_dir: Path) -> None:
    """Create income distribution plots by region."""
    setup_plot_style()
    
    # Create violin plot
    plt.figure(figsize=(15, 8))
    sns.violinplot(data=df, x='PUMA', y='median_income')
    plt.xticks(rotation=45)
    plt.title('Income Distribution by PUMA Region')
    plt.xlabel('PUMA Region')
    plt.ylabel('Median Monthly Income ($)')
    
    # Save plot
    plt.savefig(output_dir / 'income_distribution.png', bbox_inches='tight')
    plt.close()


def generate_summary_plots(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate all summary visualizations."""
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate each plot type
    plot_income_distribution(df, output_dir)
    # Add more plot functions as needed
