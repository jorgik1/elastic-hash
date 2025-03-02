"""
Setup script for backward compatibility with older pip versions.
"""
from setuptools import setup, find_packages

setup(
    name="open-elastic-hash",
    version="0.1.1",
    packages=find_packages(),
    python_requires=">=3.8",
)
