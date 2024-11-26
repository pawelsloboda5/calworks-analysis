# Analysis Methods

## Overview
This document details the analytical methods used in the CalWORKs eligibility and affordability analysis.

## 1. Eligibility Determination

### CalWORKs Eligibility Criteria
- Income thresholds based on household size
- Public assistance status
- Food stamp/SNAP participation

### Income Calculations
```python
monthly_income = annual_income / 12
eligible = monthly_income <= income_threshold[household_size]
```

## 2. Regional Analysis

### PUMA Regions (San Francisco)
- 7507: Northeast SF
- 7508: Western Addition/Marina
- 7509: Haight/Castro
- 7510: Mission/Bernal Heights
- 7511: South Central SF
- 7512: Central SF
- 7513: Northern SF
- 7514: Southeast SF

### Metrics Calculated
1. Employment Rate
2. Median Income
3. Rent Burden
4. Population Distribution

## 3. Statistical Methods

### Income Analysis
- Median calculations
- Income source aggregation
- Distribution analysis

### Affordability Metrics
- Rent-to-income ratios
- Regional comparisons
- Threshold calculations 