"""Core data model for a stock portfolio: holdings, persistence, and P/L math."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional


@dataclass
class Holding:
    """A single position in the portfolio."""

    ticker: str
    shares: float
    avg_cost: float  # average cost per share, in the portfolio's base currency

    def cost_basis(self) -> float:
        return self.shares * self.avg_cost

    def market_value(self, current_price: float) -> float:
        return self.shares * current_price

    def gain_loss(self, current_price: float) -> float:
        return self.market_value(current_price) - self.cost_basis()

    def gain_loss_pct(self, current_price: float) -> Optional[float]:
        if self.cost_basis() == 0:
            return None
        return (self.gain_loss(current_price) / self.cost_basis()) * 100


@dataclass
class Portfolio:
    """A collection of holdings, backed by a JSON file on disk."""

    holdings: dict[str, Holding] = field(default_factory=dict)
    path: Optional[Path] = None

    # ---------- persistence ----------

    @classmethod
    def load(cls, path: Path) -> "Portfolio":
        if not path.exists():
            return cls(holdings={}, path=path)
        raw = json.loads(path.read_text())
        holdings = {
            ticker: Holding(**data) for ticker, data in raw.get("holdings", {}).items()
        }
        return cls(holdings=holdings, path=path)

    def save(self) -> None:
        if self.path is None:
            raise ValueError("Portfolio has no path to save to.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"holdings": {t: asdict(h) for t, h in self.holdings.items()}}
        self.path.write_text(json.dumps(payload, indent=2))

    # ---------- mutation ----------

    def add(self, ticker: str, shares: float, price: float) -> None:
        """Add shares to a position, averaging cost if the position exists."""
        ticker = ticker.upper()
        if shares <= 0:
            raise ValueError("shares must be positive")
        if price < 0:
            raise ValueError("price cannot be negative")

        existing = self.holdings.get(ticker)
        if existing is None:
            self.holdings[ticker] = Holding(ticker=ticker, shares=shares, avg_cost=price)
            return

        total_cost = existing.cost_basis() + (shares * price)
        total_shares = existing.shares + shares
        existing.shares = total_shares
        existing.avg_cost = total_cost / total_shares

    def remove(self, ticker: str, shares: Optional[float] = None) -> None:
        """Remove shares from a position. Removes the whole position if shares is None."""
        ticker = ticker.upper()
        if ticker not in self.holdings:
            raise KeyError(f"No holding for {ticker}")

        if shares is None or shares >= self.holdings[ticker].shares:
            del self.holdings[ticker]
            return

        if shares <= 0:
            raise ValueError("shares must be positive")
        self.holdings[ticker].shares -= shares

    # ---------- reporting ----------

    def summary(self, prices: dict[str, float]) -> list[dict]:
        """Build a per-holding summary row using the given current prices."""
        rows = []
        for ticker, holding in sorted(self.holdings.items()):
            price = prices.get(ticker)
            row = {
                "ticker": ticker,
                "shares": holding.shares,
                "avg_cost": holding.avg_cost,
                "cost_basis": holding.cost_basis(),
                "price": price,
                "market_value": holding.market_value(price) if price is not None else None,
                "gain_loss": holding.gain_loss(price) if price is not None else None,
                "gain_loss_pct": holding.gain_loss_pct(price) if price is not None else None,
            }
            rows.append(row)
        return rows

    def totals(self, prices: dict[str, float]) -> dict:
        rows = self.summary(prices)
        cost_basis = sum(r["cost_basis"] for r in rows)
        market_value = sum(r["market_value"] for r in rows if r["market_value"] is not None)
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis else None
        return {
            "cost_basis": cost_basis,
            "market_value": market_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
        }
