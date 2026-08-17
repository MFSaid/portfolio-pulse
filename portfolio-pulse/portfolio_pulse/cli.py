"""Command-line interface for Portfolio Pulse.

Usage:
    portfolio-pulse add AAPL 10 150.25
    portfolio-pulse remove AAPL --shares 5
    portfolio-pulse list
    portfolio-pulse summary
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from portfolio_pulse.portfolio import Portfolio
from portfolio_pulse.price_fetcher import YFinancePriceFetcher, PriceFetcher

DEFAULT_DATA_PATH = Path.home() / ".portfolio_pulse" / "portfolio.json"


def _fmt_money(value: float | None, currency: str = "$") -> str:
    if value is None:
        return "n/a"
    return f"{currency}{value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def print_summary_table(rows: list[dict], totals: dict) -> None:
    headers = ["Ticker", "Shares", "Avg Cost", "Price", "Mkt Value", "Gain/Loss", "Gain/Loss %"]
    table_rows = []
    for r in rows:
        table_rows.append([
            r["ticker"],
            f"{r['shares']:g}",
            _fmt_money(r["avg_cost"]),
            _fmt_money(r["price"]),
            _fmt_money(r["market_value"]),
            _fmt_money(r["gain_loss"]),
            _fmt_pct(r["gain_loss_pct"]),
        ])

    widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in table_rows:
        print(fmt_row(row))

    print()
    print(f"Total cost basis:   {_fmt_money(totals['cost_basis'])}")
    print(f"Total market value: {_fmt_money(totals['market_value'])}")
    print(f"Total gain/loss:    {_fmt_money(totals['gain_loss'])} ({_fmt_pct(totals['gain_loss_pct'])})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portfolio-pulse",
        description="A lightweight command-line stock portfolio tracker.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Path to the portfolio JSON file (default: {DEFAULT_DATA_PATH})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add (or top up) shares in a position")
    add_p.add_argument("ticker")
    add_p.add_argument("shares", type=float)
    add_p.add_argument("price", type=float, help="Price per share paid")

    remove_p = subparsers.add_parser("remove", help="Remove shares from a position")
    remove_p.add_argument("ticker")
    remove_p.add_argument("--shares", type=float, default=None, help="Shares to remove (default: all)")

    subparsers.add_parser("list", help="List holdings without fetching live prices")
    subparsers.add_parser("summary", help="Show holdings with live prices and gain/loss")

    return parser


def run(argv: list[str] | None = None, price_fetcher: PriceFetcher | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    portfolio = Portfolio.load(args.data)

    if args.command == "add":
        portfolio.add(args.ticker, args.shares, args.price)
        portfolio.save()
        print(f"Added {args.shares:g} shares of {args.ticker.upper()} @ {_fmt_money(args.price)}")
        return 0

    if args.command == "remove":
        try:
            portfolio.remove(args.ticker, args.shares)
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        portfolio.save()
        print(f"Removed shares of {args.ticker.upper()}")
        return 0

    if args.command == "list":
        if not portfolio.holdings:
            print("No holdings yet. Add one with: portfolio-pulse add TICKER SHARES PRICE")
            return 0
        for ticker, h in sorted(portfolio.holdings.items()):
            print(f"{ticker}: {h.shares:g} shares @ avg cost {_fmt_money(h.avg_cost)}")
        return 0

    if args.command == "summary":
        if not portfolio.holdings:
            print("No holdings yet. Add one with: portfolio-pulse add TICKER SHARES PRICE")
            return 0
        fetcher = price_fetcher or YFinancePriceFetcher()
        prices = fetcher.get_prices(portfolio.holdings.keys())
        rows = portfolio.summary(prices)
        totals = portfolio.totals(prices)
        print_summary_table(rows, totals)
        return 0

    return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
