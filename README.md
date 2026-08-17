
# Portfolio Pulse 📈

[![Tests](https://github.com/MFSaid/portfolio-pulse/actions/workflows/tests.yml/badge.svg)](https://github.com/MFSaid/portfolio-pulse/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

A lightweight command-line tool for tracking a stock portfolio: log your buys,
pull live prices, and see gain/loss at a glance — no spreadsheet required.

## Table of contents

- [Features](#features)
- [Install](#install)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Running tests](#running-tests)
- [Possible extensions](#possible-extensions)
- [License](#license)

## Features

- **Add and remove positions** — average cost is recalculated automatically when you top up an existing holding
- **Live price lookups** via [yfinance](https://github.com/ranaroussi/yfinance) — no API key or account needed
- **Per-holding and portfolio-wide P/L**, in both currency and percentage terms
- **Plain JSON storage** — your portfolio lives in one human-readable file, easy to inspect, back up, or put under version control separately
- **Fully unit tested**, with the price fetcher swapped out for a static test double so the test suite never depends on the network
- **CI on every push** via GitHub Actions, running the test suite on Python 3.10, 3.11, and 3.12

## Install

```bash
git clone https://github.com/MFSaid/portfolio-pulse.git
cd portfolio-pulse
pip install -r requirements.txt
pip install -e .
```

This installs a `portfolio-pulse` command on your PATH. If you'd rather not
install it, you can run it directly from the repo root:

```bash
PYTHONPATH=. python -m portfolio_pulse.cli <command>
```

## Usage

```bash
# Add 10 shares of AAPL bought at $150
portfolio-pulse add AAPL 10 150

# Buying more later averages the cost automatically
portfolio-pulse add AAPL 5 160

# Remove shares (omit --shares to close the whole position)
portfolio-pulse remove AAPL --shares 5

# List holdings without hitting the network
portfolio-pulse list

# Full summary with live prices and gain/loss
portfolio-pulse summary
```

By default your portfolio is stored at `~/.portfolio_pulse/portfolio.json`.
Point at a different file with `--data path/to/file.json` if you want to keep
multiple portfolios side by side, e.g.:

```bash
portfolio-pulse --data ~/portfolios/isa.json summary
```

## How it works

- **`portfolio_pulse/portfolio.py`** — the `Holding` and `Portfolio` dataclasses. `Portfolio` handles loading/saving to JSON and all the gain/loss arithmetic (cost basis, market value, absolute and percentage gain/loss).
- **`portfolio_pulse/price_fetcher.py`** — price lookups sit behind a small `Protocol`. `YFinancePriceFetcher` hits Yahoo Finance for live prices; `StaticPriceFetcher` returns a fixed dict, which is what the test suite uses instead of making real network calls.
- **`portfolio_pulse/cli.py`** — an `argparse`-based CLI wiring the two together, plus a hand-rolled table formatter for the `summary` output.

This separation means the core logic and CLI are tested completely offline,
while the live-pricing path is a thin, swappable layer on top.

## Project structure

## Running tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/ -v
```

10 tests cover position math (adding, averaging cost, partial/full removal),
JSON save/reload round-tripping, summary/totals calculations, and the CLI
commands end-to-end using the static price fetcher.

## Possible extensions

- Multi-currency support with FX conversion
- Historical performance chart (matplotlib) exported to PNG
- CSV import/export for brokerage statements
- Dividend tracking

## License

MIT — see [LICENSE](LICENSE).
