from setuptools import setup, find_packages

setup(
    name="finmateai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "plotly>=5.18.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
) 