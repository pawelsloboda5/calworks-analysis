import pytest
import pandas as pd
from Script_python.utils.data_ops import validate_dataframe, safe_numeric_conversion, filter_by_puma

def test_validate_dataframe():
    # Create test data
    test_df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    # Test valid case
    validate_dataframe(test_df, ['col1', 'col2'], 'test_df')
    
    # Test missing column
    with pytest.raises(ValueError):
        validate_dataframe(test_df, ['col1', 'col3'], 'test_df')

def test_safe_numeric_conversion():
    test_df = pd.DataFrame({
        'numeric': ['1', '2', '3'],
        'mixed': ['1', 'a', '3']
    })
    
    result = safe_numeric_conversion(test_df, ['numeric', 'mixed'])
    assert pd.api.types.is_numeric_dtype(result['numeric'])
    assert result['mixed'].isna().sum() == 1

def test_filter_by_puma():
    test_df = pd.DataFrame({
        'PUMA': [7507, 7508, 7509, 7510]
    })
    
    result = filter_by_puma(test_df, [7507, 7508])
    assert len(result) == 2
    assert all(result['PUMA'].isin([7507, 7508])) 