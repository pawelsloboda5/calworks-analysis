import pytest
import pandas as pd
import os
from pathlib import Path
from Script_python.main import run_pipeline

@pytest.fixture
def sample_data():
    # Create minimal test data
    household_data = pd.DataFrame({
        'SERIALNO': ['1', '2'],
        'ST': [6, 6],
        'PUMA': [7507, 7508],
        'HINCP': [50000, 60000],
        'NP': [2, 3],
        'FS': [0, 1],
        'GRNTP': [2000, 2500]
    })
    
    person_data = pd.DataFrame({
        'SERIALNO': ['1', '1', '2', '2', '2'],
        'PAP': [0, 0, 1000, 0, 0],
        'WAGP': [30000, 20000, 25000, 20000, 15000],
        'SEMP': [0, 0, 0, 0, 0],
        'RETP': [0, 0, 0, 0, 0],
        'INTP': [0, 0, 0, 0, 0],
        'SSP': [0, 0, 0, 0, 0]
    })
    
    return household_data, person_data

def test_pipeline_execution(sample_data, tmp_path, monkeypatch):
    # Setup test data
    household_data, person_data = sample_data
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    
    # Save test data
    household_path = data_dir / "hca_2022.csv"
    person_path = data_dir / "pca_2022.csv"
    household_data.to_csv(household_path, index=False)
    person_data.to_csv(person_path, index=False)
    
    # Mock config paths
    monkeypatch.setenv('DATA_DIR', str(data_dir))
    monkeypatch.setenv('OUTPUT_DIR', str(output_dir))
    
    # Run pipeline
    result = run_pipeline()
    
    # Check results
    assert result == 0
    assert output_dir.exists()
    assert list(output_dir.glob("*.csv"))  # Check if any CSV files were created 