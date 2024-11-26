"""
Common data operations used across the analysis pipeline.
"""

import logging
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(
    df: pd.DataFrame, required_columns: List[str], name: str = "DataFrame"
) -> None:
    """
    Validate that a dataframe has required columns and no null values in key fields.

    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list): List of required column names
        name (str): Name of the DataFrame for error messages
    """
    logger.info(f"Validating {name}")
    logger.info(f"Available columns: {df.columns.tolist()}")

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        error_msg = f"{name} is missing required columns: {missing_cols}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    null_counts = df[required_columns].isnull().sum()
    if null_counts.any():
        logger.warning(
            f"{name} contains null values in columns: {list(null_counts[null_counts > 0].index)}"
        )


def safe_numeric_conversion(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Safely convert columns to numeric, replacing errors with NaN.

    Args:
        df (pd.DataFrame): DataFrame to process
        columns (list): List of columns to convert
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def filter_by_puma(df: pd.DataFrame, puma_codes: List[int]) -> pd.DataFrame:
    """
    Filter a dataframe by PUMA codes.

    Args:
        df (pd.DataFrame): DataFrame to filter
        puma_codes (list): List of PUMA codes to filter by
    """

    return df[df["PUMA"].isin(puma_codes)]
