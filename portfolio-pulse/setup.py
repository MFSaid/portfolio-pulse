from setuptools import setup, find_packages

setup(
    name="portfolio-pulse",
    version="0.1.0",
    description="A lightweight command-line stock portfolio tracker.",
    packages=find_packages(exclude=["tests"]),
    install_requires=["yfinance>=0.2.40"],
    entry_points={
        "console_scripts": [
            "portfolio-pulse=portfolio_pulse.cli:main",
        ],
    },
    python_requires=">=3.10",
)
