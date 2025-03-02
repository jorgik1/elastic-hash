"""
Setup script for backward compatibility with older pip versions.
"""
from setuptools import setup, find_packages

setup(
    name="elastic-hash",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
)
