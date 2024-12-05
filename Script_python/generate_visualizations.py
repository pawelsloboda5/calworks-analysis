"""Generate visualizations for CalWORKs analysis."""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)

def ensure_monthly_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Verify all required monthly income columns exist."""
    df = df.copy()
    
    # List of expected monthly columns
    monthly_cols = [
        'monthly_income',
        'monthly_PAP',
        'monthly_RETP', 
        'monthly_INTP',
        'monthly_SSP',
        'monthly_earned_income'
    ]
    
    # Check for missing columns and log warnings
    for col in monthly_cols:
        if col not in df.columns:
            logger.warning(f"Missing expected column: {col}")
            df[col] = 0
            
    return df

def plot_income_distribution(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create income distribution plot comparing eligible vs non-eligible households."""
    plt.figure(figsize=(15, 8))
    
    # Filter to reasonable income range for visibility
    plot_data = df[df['monthly_income'] <= 15000].copy()
    
    # Create distribution plot
    sns.kdeplot(
        data=plot_data,
        x='monthly_income',
        hue='eligible_calworks',
        common_norm=False,
        fill=True,
        alpha=0.5
    )
    
    plt.title('Monthly Income Distribution by CalWORKs Eligibility\nSan Francisco County, 2022', 
              fontsize=14, pad=20)
    plt.xlabel('Monthly Household Income ($)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(title='CalWORKs Eligible', labels=['No', 'Yes'], title_fontsize=12)
    
    # Add MBSAC reference lines
    mbsac_values = sorted(plot_data['MBSAC'].unique())[:3]  # Show first 3 MBSAC thresholds
    for mbsac in mbsac_values:
        plt.axvline(mbsac, color='red', linestyle='--', alpha=0.3)
        plt.text(mbsac, plt.ylim()[1], f'MBSAC: ${mbsac:,.0f}', 
                rotation=90, va='top', ha='right')
    
    # Add annotations
    plt.text(0.02, 0.98, 
            'Note: Income distribution truncated at $15,000 for visibility\n'
            'MBSAC lines show income thresholds for different household sizes',
            transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig(viz_dir / 'income_distribution.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_eligibility_by_size(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create comparative bar chart of eligibility rates by household size."""
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # Calculate eligibility rates by household size
    size_eligibility = df.groupby('NP').agg({
        'eligible_calworks': 'mean',
        'SERIALNO': 'count'
    }).reset_index()
    
    # Plot eligibility rates
    bars = ax1.bar(size_eligibility['NP'], size_eligibility['eligible_calworks'] * 100,
                   color='skyblue', alpha=0.7)
    ax1.set_xlabel('Household Size (Number of Persons)', fontsize=12)
    ax1.set_ylabel('CalWORKs Eligibility Rate (%)', fontsize=12, color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Add household count on secondary axis
    ax2 = ax1.twinx()
    line = ax2.plot(size_eligibility['NP'], size_eligibility['SERIALNO'], 
                   color='red', marker='o', linewidth=2)
    ax2.set_ylabel('Number of Households', fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Add count labels
    for x, y in zip(size_eligibility['NP'], size_eligibility['SERIALNO']):
        ax2.text(x, y, f'{int(y):,}', ha='center', va='bottom')
    
    plt.title('CalWORKs Eligibility Rate and Household Distribution by Size\n'
              'San Francisco County, 2022', fontsize=14, pad=20)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        bars.patches[0],
        Line2D([0], [0], color='red', marker='o')
    ]
    plt.legend(legend_elements, 
              ['Eligibility Rate', 'Household Count'],
              loc='upper right')
    
    # Add explanatory note
    plt.figtext(0.02, 0.02,
                'Note: Bars show the percentage of households eligible for CalWORKs at each size\n'
                'Red line shows the total number of households of each size',
                fontsize=10, ha='left')
    
    plt.savefig(viz_dir / 'eligibility_by_size.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_eligibility_heatmap(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create heatmap of eligibility rates by income and household size."""
    plt.figure(figsize=(15, 10))
    
    # Create income brackets
    income_bins = [0, 1000, 2500, 5000, 7500, 10000, float('inf')]
    income_labels = ['$0-$1,000', '$1,000-$2,500', '$2,500-$5,000', 
                    '$5,000-$7,500', '$7,500-$10,000', '$10,000+']
    
    df['income_bracket'] = pd.cut(
        df['monthly_income'],
        bins=income_bins,
        labels=income_labels
    )
    
    # Calculate eligibility rates
    heatmap_data = pd.pivot_table(
        df,
        values='eligible_calworks',
        index='income_bracket',
        columns='NP',
        aggfunc='mean'
    ) * 100
    
    # Create heatmap
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Eligibility Rate (%)', 'format': '%.0f%%'}
    )
    
    plt.title('CalWORKs Eligibility Rate by Monthly Income and Household Size\n'
              'San Francisco County, 2022', fontsize=14, pad=20)
    plt.xlabel('Household Size (Number of Persons)', fontsize=12)
    plt.ylabel('Monthly Household Income', fontsize=12)
    
    # Add explanatory note
    plt.figtext(0.02, 0.02,
                'Note: Colors show the percentage of households eligible for CalWORKs in each category\n'
                'Darker colors indicate higher eligibility rates',
                fontsize=10, ha='left')
    
    plt.savefig(viz_dir / 'eligibility_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_income_sources_breakdown(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create stacked bar chart showing income source composition by eligibility status."""
    plt.figure(figsize=(15, 8))
    
    # Define income sources with fallback columns
    income_sources = {
        'Employment': ('monthly_earned_income', 'total_earned_income'),
        'Public Assistance': ('monthly_PAP', 'PAP'),
        'Retirement': ('monthly_RETP', 'RETP'),
        'Social Security': ('monthly_SSP', 'SSP'),
        'Other': ('monthly_INTP', 'INTP')
    }
    
    # Create income data with safe column access
    income_data = {}
    for source, (monthly_col, annual_col) in income_sources.items():
        if monthly_col in df.columns:
            income_data[source] = df[monthly_col]
        elif annual_col in df.columns:
            income_data[source] = df[annual_col] / 12
        else:
            logger.warning(f"Neither {monthly_col} nor {annual_col} found. Using zeros for {source}")
            income_data[source] = pd.Series(0, index=df.index)
    
    # Convert to DataFrame
    income_data = pd.DataFrame(income_data)
    
    # Fill NaN values with 0
    income_data = income_data.fillna(0)
    
    # Calculate averages for eligible vs non-eligible
    eligible_pcts = income_data[df['eligible_calworks']].mean()
    non_eligible_pcts = income_data[~df['eligible_calworks']].mean()
    
    # Create stacked bar chart
    data = pd.DataFrame({
        'Eligible': eligible_pcts,
        'Not Eligible': non_eligible_pcts
    }).T
    
    ax = data.plot(kind='bar', stacked=True, figsize=(15, 8))
    
    plt.title('Average Monthly Income Sources by CalWORKs Eligibility Status\n'
              'San Francisco County, 2022', pad=20)
    plt.xlabel('Eligibility Status')
    plt.ylabel('Average Monthly Income ($)')
    
    # Add value labels on bars
    for c in ax.containers:
        ax.bar_label(c, fmt='${:,.0f}', label_type='center')
    
    plt.legend(title='Income Sources', bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    
    plt.savefig(viz_dir / 'income_sources_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_household_composition_analysis(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create multi-panel visualization showing household composition analysis."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Household Size Distribution
    sns.histplot(data=df, x='NP', hue='eligible_calworks', 
                multiple="dodge", shrink=.8, ax=ax1)
    ax1.set_title('Household Size Distribution by Eligibility')
    ax1.set_xlabel('Number of Persons')
    ax1.set_ylabel('Count')
    
    # 2. Working Members vs Non-Working
    working_stats = pd.DataFrame({
        'Working': [len(df[df['working_members'] > 0]),
                   len(df[df['eligible_calworks'] & (df['working_members'] > 0)])],
        'Non-Working': [len(df[df['working_members'] == 0]),
                       len(df[df['eligible_calworks'] & (df['working_members'] == 0)])]
    }, index=['All Households', 'Eligible Households'])
    
    working_stats.plot(kind='bar', ax=ax2)
    ax2.set_title('Working vs Non-Working Households')
    ax2.set_ylabel('Number of Households')
    
    # 3. Income-to-MBSAC Ratio Distribution
    df['income_to_mbsac'] = df['monthly_income'] / df['MBSAC']
    sns.kdeplot(data=df[df['income_to_mbsac'] <= 3], 
                x='income_to_mbsac', hue='eligible_calworks',
                fill=True, ax=ax3)
    ax3.axvline(x=1, color='red', linestyle='--', alpha=0.5)
    ax3.set_title('Income to MBSAC Ratio Distribution')
    ax3.set_xlabel('Income/MBSAC Ratio')
    
    # 4. Public Assistance Combinations
    assistance_types = []
    for _, row in df.iterrows():
        types = []
        if row['food_stamps_receipent']: types.append('Receiving Food Stamps')
        if row['public_assistance_receipent']: types.append('Receiving Public Assistance')
        if not types: types.append('No Current Assistance')
        assistance_types.append('+'.join(types))
    
    df['assistance_combo'] = assistance_types
    assistance_counts = df['assistance_combo'].value_counts()
    
    assistance_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax4)
    ax4.set_title('Current Assistance Program Participation')
    
    # Overall styling
    plt.suptitle('Household Composition and Assistance Analysis\nSan Francisco County, 2022', 
                fontsize=16, y=1.02)
    plt.tight_layout()
    
    plt.savefig(viz_dir / 'household_composition_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def plot_regional_metrics_dashboard(df: pd.DataFrame, viz_dir: Path) -> None:
    """Create a comprehensive regional metrics dashboard."""
    # Create PUMA-level statistics
    puma_stats = df.groupby('PUMA').agg({
        'eligible_calworks': 'mean',
        'monthly_income': 'median',
        'GRNTP': 'median',
        'working_members': 'mean',
        'NP': 'mean'
    }).reset_index()
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Eligibility Rate vs Median Income
    ax1 = axes[0, 0]
    scatter1 = ax1.scatter(puma_stats['monthly_income'], 
                          puma_stats['eligible_calworks'] * 100,
                          s=100, alpha=0.6)
    ax1.set_xlabel('Median Monthly Income ($)')
    ax1.set_ylabel('CalWORKs Eligibility Rate (%)')
    ax1.set_title('Eligibility Rate vs Median Income by PUMA')
    
    # Add PUMA labels
    for idx, row in puma_stats.iterrows():
        ax1.annotate(f"PUMA {row['PUMA']}", 
                    (row['monthly_income'], row['eligible_calworks'] * 100))
    
    # 2. Rent vs Income
    ax2 = axes[0, 1]
    scatter2 = ax2.scatter(puma_stats['monthly_income'],
                          puma_stats['GRNTP'],
                          s=100, alpha=0.6)
    ax2.set_xlabel('Median Monthly Income ($)')
    ax2.set_ylabel('Median Monthly Rent ($)')
    ax2.set_title('Rent vs Income by PUMA')
    
    # Add 30% income line
    income_range = np.linspace(0, puma_stats['monthly_income'].max(), 100)
    ax2.plot(income_range, income_range * 0.3, '--r', 
             label='30% of Income', alpha=0.5)
    ax2.legend()
    
    # 3. Employment and Household Size
    ax3 = axes[1, 0]
    scatter3 = ax3.scatter(puma_stats['working_members'],
                          puma_stats['NP'],
                          s=100, alpha=0.6)
    ax3.set_xlabel('Average Working Members')
    ax3.set_ylabel('Average Household Size')
    ax3.set_title('Employment vs Household Size by PUMA')
    
    # 4. Combined Metrics Heatmap
    ax4 = axes[1, 1]
    
    # Normalize metrics for heatmap
    heatmap_data = puma_stats.copy()
    for col in ['eligible_calworks', 'monthly_income', 'GRNTP', 
                'working_members', 'NP']:
        heatmap_data[col] = (heatmap_data[col] - heatmap_data[col].mean()) / heatmap_data[col].std()
    
    sns.heatmap(heatmap_data.set_index('PUMA')
                .rename(columns={
                    'eligible_calworks': 'Eligibility Rate',
                    'monthly_income': 'Income',
                    'GRNTP': 'Rent',
                    'working_members': 'Working Members',
                    'NP': 'Household Size'
                }),
                cmap='RdYlBu', center=0, ax=ax4)
    ax4.set_title('Standardized Regional Metrics Heatmap')
    
    plt.suptitle('Regional Analysis Dashboard\nSan Francisco County, 2022', 
                 fontsize=16, y=1.02)
    plt.tight_layout()
    
    plt.savefig(viz_dir / 'regional_metrics_dashboard.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def generate_all_visualizations(df: pd.DataFrame, viz_dir: Path) -> None:
    """Generate all visualizations."""
    logger.info("Generating visualizations...")
    
    try:
        # Create visualization directory
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure all required monthly columns exist
        df = ensure_monthly_columns(df)
        
        # Generate existing visualizations
        plot_income_distribution(df, viz_dir)
        plot_eligibility_by_size(df, viz_dir)
        plot_eligibility_heatmap(df, viz_dir)
        
        # Generate new visualizations
        plot_income_sources_breakdown(df, viz_dir)
        plot_household_composition_analysis(df, viz_dir)
        plot_regional_metrics_dashboard(df, viz_dir)
        
        logger.info(f"Successfully generated visualizations in {viz_dir}")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        raise