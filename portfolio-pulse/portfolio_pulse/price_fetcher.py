"""Fetches current prices for tickers. Isolated behind a small interface so it
can be swapped out or mocked easily (e.g. in tests, or for a different data source).
"""

from __future__ import annotations

from typing import Iterable, Protocol


class PriceFetcher(Protocol):
    def get_prices(self, tickers: Iterable[str]) -> dict[str, float]:
        ...


class YFinancePriceFetcher:
    """Fetches live prices using the yfinance library (no API key required)."""

    def get_prices(self, tickers: Iterable[str]) -> dict[str, float]:
        tickers = list(dict.fromkeys(t.upper() for t in tickers))  # dedupe, keep order
        if not tickers:
            return {}

        try:
            import yfinance as yf
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "yfinance is not installed. Run: pip install -r requirements.txt"
            ) from exc

        prices: dict[str, float] = {}
        data = yf.Tickers(" ".join(tickers))
        for ticker in tickers:
            try:
                fast_info = data.tickers[ticker].fast_info
                price = fast_info.get("last_price") or fast_info.get("lastPrice")
                if price is not None:
                    prices[ticker] = float(price)
            except Exception:
                # Skip tickers that fail to fetch (bad symbol, network hiccup, etc.)
                continue
        return prices


class StaticPriceFetcher:
    """A fixed-price fetcher, useful for tests, demos, or offline use."""

    def __init__(self, prices: dict[str, float]):
        self._prices = {t.upper(): p for t, p in prices.items()}

    def get_prices(self, tickers: Iterable[str]) -> dict[str, float]:
        return {t.upper(): self._prices[t.upper()] for t in tickers if t.upper() in self._prices}
