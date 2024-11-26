from pathlib import Path

import pandas as pd
import pytest

from Script_python.main import run_pipeline
from Script_python.utils.config import load_config


@pytest.fixture
def sample_data():
    # Create sample household data
    household_data = pd.DataFrame(
        {
            "SERIALNO": ["1", "2", "3", "4", "5"],
            "ST": [6, 6, 6, 6, 6],
            "PUMA": [7507, 7508, 7509, 7510, 7511],
            "HINCP": [50000, 60000, 30000, 20000, 15000],
            "NP": [2, 3, 1, 2, 2],
            "FS": [0, 1, 0, 0, 1],
            "GRNTP": [2000, 2500, 1500, 1800, 1600],
        }
    )

    # Create sample person data with matching SERIALNO and PUMA
    person_data = pd.DataFrame(
        {
            "SERIALNO": ["1", "1", "2", "2", "2"],
            "PUMA": [7507, 7507, 7508, 7508, 7508],
            "PAP": [0, 0, 1000, 0, 0],
            "WAGP": [30000, 20000, 25000, 20000, 15000],
            "SEMP": [0, 0, 0, 0, 0],
            "RETP": [0, 0, 0, 0, 0],
            "INTP": [0, 0, 0, 0, 0],
            "SSP": [0, 0, 0, 0, 0],
        }
    )

    return household_data, person_data


def test_pipeline_execution(sample_data, tmp_path, monkeypatch):
    """Test the complete analysis pipeline."""
    # Setup test data
    household_data, person_data = sample_data

    # Create test directories
    data_dir = tmp_path / "Script_python" / "data"
    data_dir.mkdir(parents=True)
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    plots_dir = tmp_path / "plots"
    plots_dir.mkdir(parents=True)

    # Save test data
    household_path = data_dir / "hca_2022.csv"
    person_path = data_dir / "pca_2022.csv"
    household_data.to_csv(household_path, index=False)
    person_data.to_csv(person_path, index=False)

    # Create test config
    test_config = {
        "paths": {
            "household_data": str(household_path),
            "person_data": str(person_path),
            "output_dir": str(output_dir),
            "plots_dir": str(plots_dir),
            "eligible_households": str(output_dir / "eligible_households.csv"),
            "eligible_persons": str(output_dir / "eligible_persons.csv"),
        }
    }

    # Mock config loading
    def mock_load_config():
        return test_config

    monkeypatch.setattr("Script_python.main.load_config", mock_load_config)

    # Run pipeline
    result = run_pipeline()

    # Check results
    assert result == 0
    assert (output_dir / "eligible_households.csv").exists()
    assert (output_dir / "eligible_persons.csv").exists()
