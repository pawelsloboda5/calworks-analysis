# Data Features & Pipeline Steps

## Pipeline Steps and Generated Features

### 1. Preprocessing (preprocessing.py)
Initial Data Features:
- `SERIALNO`: Household identifier
- `ST`: State code
- `PUMA`: Geographic region code
- `NP`: Number of persons
- `HINCP`: Household income
- `FS`: Food stamps status
- `GRNTP`: Gross rent

### 2. Income Filtering (income_filtering.py)
Added Income Features:
- `monthly_income`: HINCP divided by 12
- `earned_income`: Sum of WAGP + SEMP
- `unearned_income`: Sum of RETP + INTP + PAP + SSP
- `earned_income_after_disregard`: Applied $450 disregard
- `total_countable_income`: Final income calculation
- `working_members`: Count of employed household members

### 3. Eligibility Calculation (preprocessing.py)
Eligibility Features:
- `income_eligible`: Below MBSAC threshold
- `food_stamps_receipent`: Receives food stamps
- `public_assistance_receipent`: Receives public assistance
- `eligible_calworks`: Overall eligibility flag
- `MBSAC`: Minimum Basic Standard of Adequate Care threshold

### 4. Regional Analysis (regions_afford.py)
Regional Metrics:
- `median_rent`: By PUMA region
- `median_income`: By PUMA region
- `median_income_to_rent_ratio`: Affordability metric
- `households_with_employment_income`: Employment stats
- `avg_household_size`: Demographics
- `total_households`: Regional counts

### 5. Visualization Features (generate_plotly.py, generate_visualizations.py)
Interactive Elements:
- Income distribution curves
- Eligibility flow diagrams
- Regional comparison charts
- Household size distributions
- Employment status breakdowns

## Output Directory Structure
```
after_main_run_logs/
├── [timestamp]_[region]_HH[count]_P[count]/
│   ├── final_statistics.json
│   ├── data_loading_stats.txt
│   ├── income_metrics.txt
│   ├── eligibility_stats.txt
│   ├── regional_analysis.txt
│   └── visualizations/
│       ├── plotly/
│       │   └── eligibility_flow.html
│       └── static/
│           ├── income_distribution.png
│           ├── eligibility_by_size.png
│           └── eligibility_heatmap.png
``` 