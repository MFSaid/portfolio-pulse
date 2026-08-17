import json
import tempfile
from pathlib import Path

import pytest

from portfolio_pulse.portfolio import Portfolio, Holding
from portfolio_pulse.price_fetcher import StaticPriceFetcher
from portfolio_pulse.cli import run


@pytest.fixture
def tmp_path_file(tmp_path):
    return tmp_path / "portfolio.json"


def test_add_new_holding(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    p.add("aapl", 10, 100)
    assert p.holdings["AAPL"].shares == 10
    assert p.holdings["AAPL"].avg_cost == 100


def test_add_averages_cost(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    p.add("AAPL", 10, 100)
    p.add("AAPL", 10, 200)
    h = p.holdings["AAPL"]
    assert h.shares == 20
    assert h.avg_cost == pytest.approx(150)


def test_add_rejects_invalid_input(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    with pytest.raises(ValueError):
        p.add("AAPL", -1, 100)
    with pytest.raises(ValueError):
        p.add("AAPL", 1, -5)


def test_remove_partial(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    p.add("AAPL", 10, 100)
    p.remove("AAPL", 4)
    assert p.holdings["AAPL"].shares == 6


def test_remove_all_deletes_holding(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    p.add("AAPL", 10, 100)
    p.remove("AAPL")
    assert "AAPL" not in p.holdings


def test_remove_missing_raises(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    with pytest.raises(KeyError):
        p.remove("MSFT")


def test_save_and_reload_roundtrip(tmp_path_file):
    p = Portfolio.load(tmp_path_file)
    p.add("AAPL", 10, 100)
    p.add("MSFT", 5, 300)
    p.save()

    reloaded = Portfolio.load(tmp_path_file)
    assert reloaded.holdings["AAPL"].shares == 10
    assert reloaded.holdings["MSFT"].avg_cost == 300


def test_summary_and_totals_math():
    p = Portfolio()
    p.add("AAPL", 10, 100)  # cost basis 1000
    p.add("MSFT", 5, 300)   # cost basis 1500

    prices = {"AAPL": 120, "MSFT": 280}
    rows = p.summary(prices)
    totals = p.totals(prices)

    aapl = next(r for r in rows if r["ticker"] == "AAPL")
    assert aapl["market_value"] == 1200
    assert aapl["gain_loss"] == 200
    assert aapl["gain_loss_pct"] == pytest.approx(20.0)

    assert totals["cost_basis"] == 2500
    assert totals["market_value"] == 2600
    assert totals["gain_loss"] == 100


def test_cli_add_and_list(tmp_path_file, capsys):
    exit_code = run(["--data", str(tmp_path_file), "add", "AAPL", "10", "150"])
    assert exit_code == 0
    exit_code = run(["--data", str(tmp_path_file), "list"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "AAPL" in out


def test_cli_summary_uses_injected_fetcher(tmp_path_file, capsys):
    run(["--data", str(tmp_path_file), "add", "AAPL", "10", "100"])
    fetcher = StaticPriceFetcher({"AAPL": 150})
    exit_code = run(["--data", str(tmp_path_file), "summary"], price_fetcher=fetcher)
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "AAPL" in out
    assert "500" in out  # gain of (150-100)*10 = 500
