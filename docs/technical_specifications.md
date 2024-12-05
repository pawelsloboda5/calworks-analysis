# Technical Specifications

## Data Processing Pipeline

### 1. Data Preprocessing
```python
# Input validation
- Validate column presence
- Check data types
- Handle missing values
- Filter SF PUMA regions (7507-7514) or change in config.yaml

# Data cleaning
- Convert numeric columns
- Remove duplicates
- Validate SERIALNO matching
```

### 2. Eligibility Calculation
```python
# MBSAC Thresholds (Monthly)
{
    1: 899,  2: 1476, 3: 1829,
    4: 2170, 5: 2476, 6: 2785,
    7: 3061, 8: 3331, 9: 3614,
    10: 3922,
    'additional_person': 308
}

# Eligibility Rules
eligible = (
    (monthly_income <= mbsac_threshold) OR
    (has_public_assistance) OR
    (receives_food_stamps)
)
```

### 3. Income Analysis
```python
# Income Sources
- Employment: WAGP + SEMP
- Public Assistance: PAP
- Retirement: RETP
- Dividends: INTP
- Social Security: SSP

# Aggregation Methods
- Per Household: Sum of all member incomes
- Per Region: Median of household values
```

### 4. Visualization Specifications
```python
# Static Plot Configurations
- DPI: 300
- Figure Size: (15, 8)
- Font Size: Title=14, Labels=12
- Color Palette: "YlOrRd"

# Interactive Plot Configurations
- Plotly HTML output
- Responsive design
- Custom hover templates
- Color scales: "Viridis"
```

## Performance Requirements

### Memory Usage
- Peak memory: < 4GB
- Dataset size: < 1GB
- Batch processing: 10,000 records

### Processing Time
- Full pipeline: < 1 minutes
- Data loading: < 30 seconds
- Visualization: < 20 seconds

### Scalability
- Max households: 500,000
- Max persons: 1,000,000
- PUMA regions: 8-12

## Error Handling

### Data Validation
```python
# Required column checks
validate_dataframe(df, required_columns)

# Numeric conversion
safe_numeric_conversion(df, numeric_columns)

# Range validation
validate_ranges(df, range_specs)
```

### Error Logging
- Level: INFO, WARNING, ERROR
- File: processing.log
- Format: timestamp, level, message
- Detailed transformation tracking

## Dependencies
```requirements
pandas>=2.1.3
numpy>=1.26.2
matplotlib>=3.8.2
seaborn>=0.13.0
plotly>=5.18.0
PyYAML>=6.0.1
```

## Output Specifications

### Data Files
- UTF-8 encoding
- No index
- Headers included
- Comma-separated
- Timestamped directories

### Visualizations
- Static: PNG (300 DPI)
- Interactive: HTML
- Size: 15x8 inches
- Color: RGB