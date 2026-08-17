# Portfolio Pulse 📈

A lightweight command-line tool for tracking a stock portfolio: log your buys,
pull live prices, and see gain/loss at a glance — no spreadsheet required.

```
Ticker  Shares  Avg Cost  Price    Mkt Value  Gain/Loss  Gain/Loss %
------  ------  --------  -------  ---------  ---------  -----------
AAPL    10      $150.00   $178.32  $1,783.20  $283.20    +18.88%
MSFT    5       $300.00   $295.10  $1,475.50  $-24.50    -1.63%
TSLA    8       $220.00   $250.75  $2,006.00  $246.00    +13.98%

Total cost basis:   $4,760.00
Total market value: $5,264.70
Total gain/loss:    $504.70 (+10.60%)
```

## Features

- Add and remove positions, with automatic average-cost calculation on top-ups
- Live price lookups via [yfinance](https://github.com/ranaroussi/yfinance) — no API key needed
- Per-holding and portfolio-wide gain/loss, in £/$ and %
- Portfolio stored as plain JSON — easy to inspect, back up, or version
- Fully unit tested, with the price fetcher mocked out so tests never hit the network

## Install

```bash
git clone https://github.com/<your-username>/portfolio-pulse.git
cd portfolio-pulse
pip install -r requirements.txt
pip install -e .
```

This installs a `portfolio-pulse` command on your PATH. Alternatively, run it
directly without installing:

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
Point at a different file with `--data path/to/file.json`, e.g. to keep
multiple portfolios side by side.

## Project structure

```
portfolio_pulse/
├── portfolio.py       # Holding/Portfolio data model, JSON persistence, P/L math
├── price_fetcher.py   # Live price lookups (yfinance), swappable for testing
└── cli.py             # argparse-based command-line interface
tests/
└── test_portfolio.py  # Unit tests for the model, CLI, and math
```

The price fetcher is defined behind a small `Protocol`, so `summary` can be
tested end-to-end with a `StaticPriceFetcher` instead of hitting a real API —
no flaky network calls in CI.

## Running tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/ -v
```

Tests run automatically on push via GitHub Actions (`.github/workflows/tests.yml`).

## Possible extensions

- Multi-currency support with FX conversion
- Historical performance chart (matplotlib) exported to PNG
- CSV import/export for brokerage statements
- Dividend tracking

## License

MIT — see [LICENSE](LICENSE).
