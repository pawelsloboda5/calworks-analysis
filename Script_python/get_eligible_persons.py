# Step 2 of the preprocessing script is to filter for households in San Francisco and save the results to a CSV file. The script uses the following code snippet to filter households in San Francisco:
# get_eligible_persons.py : Filter persons under eligible households and save to a CSV.
# Location: Script_python/preprocessing.py
# CSF files: data/eligible_calworks_sf_households.csv, data/pca_2022.csv, data/eligible_calworks_sf_persons.csv
# Output: eligible_calworks_sf_persons.csv
#
from pathlib import Path

import pandas as pd


def save_eligible_persons(person_df: pd.DataFrame, eligible_households: pd.DataFrame) -> pd.DataFrame:
    """
    Filter persons under eligible households and save to a CSV.
    
    Args:
        person_df (pd.DataFrame): DataFrame containing person data
        eligible_households (pd.DataFrame): DataFrame containing eligible households
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing only eligible persons
    """
    # Filter persons based on SERIALNO in eligible households
    eligible_persons = person_df[person_df['SERIALNO'].isin(eligible_households['SERIALNO'])]
    return eligible_persons

# When running as standalone script
if __name__ == "__main__":
    # Get the project root directory (2 levels up from this script)
    project_root = Path(__file__).parent.parent
    
    # Define paths relative to project root
    household_data_path = project_root / 'Script_python/data/eligible_calworks_sf_households.csv'
    person_data_path = project_root / 'Script_python/data/pca_2022.csv'
    output_path = project_root / 'Script_python/data/eligible_calworks_sf_persons.csv'

    # Load data
    eligible_households = pd.read_csv(household_data_path, low_memory=False)
    person_df = pd.read_csv(person_data_path, low_memory=False)

    # Save eligible persons
    eligible_persons = save_eligible_persons(person_df, eligible_households)
    eligible_persons.to_csv(output_path, index=False)

    # Display summary
    print(eligible_persons.head())
