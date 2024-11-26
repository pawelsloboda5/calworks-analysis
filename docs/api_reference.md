# API Reference

## Core Modules

### preprocessing

#### `load_pums_data(household_data_path: str, person_data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]`
Loads and validates PUMS data files.

**Parameters:**
- `household_data_path`: Path to household PUMS data CSV
- `person_data_path`: Path to person PUMS data CSV

**Returns:**
- Tuple of (household_df, person_df)

**Example:**
```python
from preprocessing import load_pums_data
household_df, person_df = load_pums_data('data/hca_2022.csv', 'data/pca_2022.csv')
```

#### `calculate_eligibility(household_df: pd.DataFrame, aggregated_person_df: pd.DataFrame) -> pd.DataFrame`
Determines CalWORKs eligibility for households.

**Parameters:**
- `household_df`: Processed household data
- `aggregated_person_df`: Aggregated person-level data

**Returns:**
- DataFrame of eligible households

### income_filtering

#### `calculate_income_metrics(config: Dict) -> pd.DataFrame`
Calculates income-related metrics for households.

**Parameters:**
- `config`: Configuration dictionary containing paths and parameters

**Returns:**
- DataFrame with income metrics

### regions_afford

#### `analyze_regions(eligible_households: pd.DataFrame, eligible_persons: pd.DataFrame) -> pd.DataFrame`
Analyzes affordability metrics by PUMA region.

**Parameters:**
- `eligible_households`: Eligible household data
- `eligible_persons`: Eligible person data

**Returns:**
- Regional analysis summary

## Utility Modules

### utils.data_ops

#### `validate_dataframe(df: pd.DataFrame, required_columns: List[str], name: str = "DataFrame") -> None`
Validates DataFrame structure and content.

**Parameters:**
- `df`: DataFrame to validate
- `required_columns`: List of required column names
- `name`: Name for error messages

#### `safe_numeric_conversion(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame`
Safely converts columns to numeric type.

**Parameters:**
- `df`: Input DataFrame
- `columns`: List of columns to convert

**Returns:**
- DataFrame with converted columns

### utils.config

#### `setup_logging() -> logging.Logger`
Configures logging for the application.

**Returns:**
- Configured logger instance

#### `load_config(config_path: str = 'config.yaml') -> Dict`
Loads configuration from YAML file.

**Parameters:**
- `config_path`: Path to configuration file

**Returns:**
- Configuration dictionary

## Visualization Modules

### visualizations.plots

#### `plot_income_distribution(df: pd.DataFrame, output_dir: Path) -> None`
Generates income distribution plots.

**Parameters:**
- `df`: Regional summary data
- `output_dir`: Output directory for plots

#### `plot_income_sources(df: pd.DataFrame, output_dir: Path) -> None`
Generates income source comparison plots.

**Parameters:**
- `df`: Regional summary data
- `output_dir`: Output directory for plots

#### `plot_rent_burden(df: pd.DataFrame, output_dir: Path) -> None`
Generates rent burden analysis plots.

**Parameters:**
- `df`: Regional summary data
- `output_dir`: Output directory for plots

#### `plot_household_stats(df: pd.DataFrame, output_dir: Path) -> None`
Generates household statistics plots.

**Parameters:**
- `df`: Regional summary data
- `output_dir`: Output directory for plots

## Pipeline Execution

### main

#### `run_pipeline() -> int`
Executes the complete analysis pipeline.

**Returns:**
- 0 on success, 1 on failure

**Example:**
```python
from main import run_pipeline
exit_code = run_pipeline()
```

## Usage Scenarios

### 1. Basic Eligibility Analysis
```python
from preprocessing import load_pums_data, calculate_eligibility
from utils.config import load_config

# Load configuration
config = load_config()

# Load and process data
household_df, person_df = load_pums_data(
    config['paths']['household_data'],
    config['paths']['person_data']
)

# Calculate eligibility
eligible_households = calculate_eligibility(household_df, person_df)
print(f"Found {len(eligible_households)} eligible households")
```

### 2. Regional Income Analysis
```python
from income_filtering import calculate_income_metrics
from regions_afford import analyze_regions

# Calculate income metrics
households_with_income = calculate_income_metrics(config)

# Analyze regions
region_summary = analyze_regions(households_with_income, eligible_persons)

# Print summary statistics
print("\nMedian Income by Region:")
for _, row in region_summary.iterrows():
    print(f"PUMA {row['PUMA']}: ${row['median_income']:,.2f}")
```

### 3. Custom Visualization
```python
from visualizations.plots import setup_plot_style
import matplotlib.pyplot as plt
import seaborn as sns

# Create custom visualization
def plot_income_vs_rent(df, output_dir):
    setup_plot_style()
    plt.figure(figsize=(12, 6))
    
    sns.scatterplot(
        data=df,
        x='median_income',
        y='median_rent',
        hue='PUMA'
    )
    
    plt.title('Income vs Rent by Region')
    plt.xlabel('Median Monthly Income ($)')
    plt.ylabel('Median Monthly Rent ($)')
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'income_vs_rent.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### 4. Data Validation Example
```python
from utils.data_ops import validate_dataframe, safe_numeric_conversion

# Define required columns
required_household_cols = ['SERIALNO', 'ST', 'PUMA', 'HINCP', 'NP', 'FS', 'GRNTP']
required_person_cols = ['SERIALNO', 'PAP', 'WAGP', 'SEMP', 'RETP', 'INTP', 'SSP']

# Validate data
validate_dataframe(household_df, required_household_cols, 'Household Data')
validate_dataframe(person_df, required_person_cols, 'Person Data')

# Convert numeric columns
numeric_cols = ['HINCP', 'GRNTP']
household_df = safe_numeric_conversion(household_df, numeric_cols)
```

### 5. Full Pipeline with Error Handling
```python
import logging
from pathlib import Path

def run_analysis(config_path: str = 'config.yaml') -> bool:
    try:
        # Setup
        config = load_config(config_path)
        logger = setup_logging()
        
        # Create output directory
        output_dir = Path(config['paths']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load and process data
        household_df, person_df = load_pums_data(
            config['paths']['household_data'],
            config['paths']['person_data']
        )
        
        # Calculate eligibility
        eligible_households = calculate_eligibility(household_df, person_df)
        
        # Analyze income and regions
        households_with_income = calculate_income_metrics(config)
        region_summary = analyze_regions(
            households_with_income,
            eligible_persons
        )
        
        # Generate visualizations
        generate_summary_plots(region_summary, output_dir)
        
        logger.info("Analysis completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return False
```

### 6. Batch Processing Example
```python
def process_multiple_regions(puma_codes: List[int]) -> Dict[int, pd.DataFrame]:
    results = {}
    
    for puma in puma_codes:
        # Filter data for specific PUMA
        region_households = household_df[household_df['PUMA'] == puma]
        region_persons = person_df[
            person_df['SERIALNO'].isin(region_households['SERIALNO'])
        ]
        
        # Process region
        eligible = calculate_eligibility(region_households, region_persons)
        results[puma] = eligible
    
    return results

# Usage
sf_pumas = [7507, 7508, 7509, 7510, 7511, 7512, 7513, 7514]
regional_results = process_multiple_regions(sf_pumas)
```

### 7. Configuration Management
```python
# Custom configuration example
custom_config = {
    'paths': {
        'household_data': 'data/custom_household.csv',
        'person_data': 'data/custom_person.csv',
        'output_dir': 'custom_output'
    },
    'analysis': {
        'min_household_size': 1,
        'max_household_size': 10,
        'income_percentile_cutoff': 95
    },
    'sf_puma_codes': [7507, 7508, 7509, 7510]
}

# Save custom configuration
import yaml
with open('custom_config.yaml', 'w') as f:
    yaml.dump(custom_config, f)

# Run analysis with custom config
run_analysis('custom_config.yaml')
```

## Data Structures

### Household Data
```python
{
    'SERIALNO': str,      # Household identifier
    'ST': int,           # State code
    'PUMA': int,         # PUMA region code
    'HINCP': float,      # Household income
    'NP': int,           # Number of persons
    'FS': int,           # Food stamp status
    'GRNTP': float       # Gross rent
}
```

### Person Data
```python
{
    'SERIALNO': str,     # Household identifier
    'PAP': float,        # Public assistance income
    'WAGP': float,       # Wages/salary income
    'SEMP': float,       # Self-employment income
    'RETP': float,       # Retirement income
    'INTP': float,       # Interest income
    'SSP': float         # Social Security income
} 