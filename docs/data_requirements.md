# Data Requirements

## Required Files and Formats

### Household Data (hca_2022.csv)
Required columns:
- **SERIALNO**: Unique household identifier (string)
- **ST**: State code (must be 6 for California)
- **PUMA**: Public Use Microdata Area code (7507-7514 for SF)
- **HINCP**: Household income (numeric)
- **NP**: Number of persons in household (1-10)
- **FS**: Food Stamp/SNAP status (0 or 1)
- **GRNTP**: Gross rent (numeric)

### Person Data (pca_2022.csv)
Required columns:
- **SERIALNO**: Household identifier (matches household data)
- **PAP**: Public Assistance income (numeric)
- **WAGP**: Wages/salary income (numeric)
- **SEMP**: Self-employment income (numeric)
- **RETP**: Retirement income (numeric)
- **INTP**: Interest income (numeric)
- **SSP**: Social Security income (numeric)

## Data Format Specifications

### Numeric Values
- All income values should be annual amounts in USD
- Missing values should be coded as 0 or null
- Negative values are not accepted

### Categorical Values
- **ST** (State): Must be 6 (California)
- **PUMA** (Region): Must be one of [7507, 7508, 7509, 7510, 7511, 7512, 7513, 7514]
- **FS** (Food Stamps): 0 = No, 1 = Yes

### Data Quality Requirements
1. No duplicate SERIALNO values in household data
2. All SERIALNO values in person data must exist in household data
3. No negative income values
4. No missing values in key fields (SERIALNO, ST, PUMA)

## Sample Data Format

### hca_2022.csv
```csv
SERIALNO,ST,PUMA,HINCP,NP,FS,GRNTP
"2022GQ000001",6,7507,50000,2,0,2000
"2022GQ000002",6,7508,60000,3,1,2500
```

### pca_2022.csv
```csv
SERIALNO,PAP,WAGP,SEMP,RETP,INTP,SSP
"2022GQ000001",0,30000,0,0,0,0
"2022GQ000001",0,20000,0,0,0,0
"2022GQ000002",1000,25000,0,0,0,0
```

## Data Sources
- Data should be obtained from the U.S. Census Bureau's Public Use Microdata Sample (PUMS)
- Use the most recent available year (currently 2022)
- California state-specific PUMS data