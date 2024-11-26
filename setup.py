# setup.py
# This file is used to create a Python package from the Script_python directory.
# It is used to install the package and its dependencies.

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="calworks-analysis",
    version="1.0.0",
    author="Pawel Sloboda",
    author_email="your.email@example.com",
    description="Analysis of CalWORKs eligibility and regional affordability in San Francisco",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pawelsloboda/calworks-analysis",
    packages=find_packages(where="Script_python"),
    package_dir={"": "Script_python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        'pandas>=1.5.3,<2.0.0',
        'numpy>=1.24.3,<2.0.0',
        'PyYAML==6.0.1',
        'matplotlib>=3.7.1,<4.0.0',
        'seaborn>=0.12.2,<1.0.0',
        'scipy>=1.10.1,<2.0.0',
    ],
    entry_points={
        "console_scripts": [
            "calworks-analysis=main:run_pipeline",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.yaml"],
    },
) 