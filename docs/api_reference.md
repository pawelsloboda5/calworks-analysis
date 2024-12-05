# CalWORKs Analysis Pipeline API Reference

## Main Components

### Main Pipeline (main.py)

The central script that orchestrates the entire analysis process.

```python
from Script_python.main import run_pipeline
exit_code = run_pipeline()
```

Key Features:
- Creates timestamped output directories
- Generates detailed statistics and visualizations
- Saves transformation logs
- Handles errors gracefully

### Data Processing

#### Preprocessing (preprocessing.py)
Handles initial data loading and cleaning:

```python
from Script_python.preprocessing import load_pums_data
household_df, person_df = load_pums_data()
```

#### Income Analysis (income_filtering.py)
Calculates household income metrics:
- Monthly and annual income
- Employment status
- Public assistance
- Income eligibility

#### Regional Analysis (regions_afford.py)
Analyzes data by geographic region:
- Median income by area
- Housing costs
- Employment rates
- Public assistance rates

### Visualizations

#### Static Plots (generate_visualizations.py)
Creates standard matplotlib/seaborn plots:
- Income distribution
- Eligibility by household size
- Regional comparisons

```python
from Script_python.generate_visualizations import generate_all_visualizations
generate_all_visualizations(data, output_dir)
```

#### Interactive Plots (generate_plotly.py)
Creates interactive Plotly visualizations:
- Eligibility flow diagram
- Income pathways
- Interactive regional maps

```python
from Script_python.generate_plotly import generate_all_plotly_visualizations
generate_all_plotly_visualizations(data, viz_dir)
```

Key Features:
- Hover information
- Zoomable interfaces
- Exportable to HTML

## Output Structure

### Statistics Files
- `final_statistics.json`: Complete analysis results
- `data_loading_stats.txt`: Initial data metrics
- `income_metrics.txt`: Income analysis results
- `eligibility_stats.txt`: Eligibility breakdown
- `regional_analysis.txt`: Geographic analysis

### Visualizations
Located in `visualizations/` directory:
- Static PNG plots
- Interactive HTML plots
- Data flow diagrams

## Configuration

### Config File (config.yaml)
Controls pipeline settings:

```yaml
pipeline:
  version: "1.1.2"
  state_code: 6  # California

paths:
  household_data: "data/hca_2022.csv"
  person_data: "data/pca_2022.csv"
```

### Logging
Automatic logging of:
- Processing steps
- Data transformations
- Error messages
- Execution time

## Basic Usage

1. Run Complete Analysis:

```python
python run_analysis.py
```

2. Generate Only Visualizations:

```python
from Script_python.generate_visualizations import generate_all_visualizations
from Script_python.generate_plotly import generate_all_plotly_visualizations

generate_all_visualizations(data, "output/viz")
generate_all_plotly_visualizations(data, "output/interactive")
```

3. Access Results:

```python
import json
with open("output/final_statistics.json") as f:
    results = json.load(f)
```

## Common Use Cases

### 1. Basic Analysis

```python
from Script_python.main import run_pipeline
run_pipeline()  # Runs everything with default settings
```

### 2. Custom Region Analysis

```python
from Script_python.regions_afford import analyze_regions
region_summary = analyze_regions(household_data, person_data)
```

### 3. Income Analysis

```python
from Script_python.income_filtering import calculate_income_metrics
income_stats = calculate_income_metrics(household_data, person_data)
```

## Error Handling

The pipeline includes comprehensive error handling:
- Data validation
- Missing file checks
- Numeric conversion safety
- Detailed error messages

## Output Examples

### Statistics Output

```json
{
    "region_summary": {
        "total_households": 4479,
        "calworks_eligible": 1127,
        "median_monthly_income": "$8,333.33"
    }
}
```

### Visualization Output
- Income distribution plots
- Eligibility flow diagrams
- Regional comparison charts
- Interactive dashboards

## Getting Help

For issues or questions:
1. Check the logs in the output directory
2. Review error messages in console
3. Examine transformation logs
4. Verify input data format
