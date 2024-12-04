# setup.py
# This file is used to create a Python package from the Script_python directory.
# It is used to install the package and its dependencies.

from setuptools import setup, find_packages

setup(
    name="calworks-analysis",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.3",
        "numpy>=1.24.3",
        "PyYAML==6.0.1",
        "matplotlib>=3.7.1",
        "seaborn>=0.12.2",
        "scipy>=1.10.1",
    ],
)
