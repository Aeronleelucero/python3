import argparse
import csv
import math
from datetime import datetime
from pathlib import Path

PORTFOLIO_FILE = Path(__file__).resolve().parent / "portfolio_summary.csv"

SAMPLE_PRICES = {
    "AAPL": 250.00,
    "MSFT": 510.00,
    "NVDA": 180.00,
    "AMZN": 225.00,
    "GOOGL": 200.00,
}

CSV_FIELDS = [
    "timestamp",
    "ticker",
    "shares",
    "buy_price",
    "current_price",
    "invested",
    "market_value",
    "gain_loss",
    "return_percent",
]

TABLE_WIDTH = 71


def get_current_price(ticker, live=False):
    if not live:
        if ticker not in SAMPLE_PRICES:
            raise ValueError(f"No sample price available for {ticker}.")
        return SAMPLE_PRICES[ticker]

    try:
        import yfinance as yf
    except ImportError as error:
        raise RuntimeError(
            "Install live-price support with: python -m pip install yfinance"
        ) from error

    closes = yf.Ticker(ticker).history(period="5d")["Close"].dropna()

    if closes.empty:
        raise ValueError(f"No market price available for {ticker}.")

    price = float(closes.iloc[-1])

    if price <= 0:
        raise ValueError(f"Invalid market price for {ticker}.")

    return price


def get_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Enter a valid number.")
            continue

        if math.isfinite(value) and value > 0:
            return value

        print("Enter a number greater than zero.")


def add_position(portfolio, ticker, buy_price, shares):
    if ticker in portfolio:
        old = portfolio[ticker]
        total_shares = old["shares"] + shares
        buy_price = (
            old["buy_price"] * old["shares"] + buy_price * shares
        ) / total_shares
        shares = total_shares

    portfolio[ticker] = {"buy_price": buy_price, "shares": shares}


def collect_portfolio():
    portfolio = {}

    print("\nInvestment Portfolio Tracker")
    print("Enter DONE as the ticker when finished.\n")

    while True:
        ticker = input("Stock ticker: ").strip().upper()

        if ticker == "DONE":
            return portfolio

        if not ticker.isascii() or not ticker.isalpha():
            print("Enter a valid ticker using letters A-Z.")
            continue

        buy_price = get_positive_number("Buy price per share: ")
        shares = get_positive_number("Number of shares: ")

        add_position(portfolio, ticker, buy_price, shares)
        print(f"Added {shares:g} shares of {ticker}.\n")


def calculate_portfolio(portfolio, live=False):
    results = []

    print(
        f"\n{'Ticker':<10}{'Shares':>10}{'Buy Price':>13}"
        f"{'Current':>13}{'Gain/Loss':>14}{'Return':>11}"
    )
    print("-" * TABLE_WIDTH)

    for ticker, position in portfolio.items():
        try:
            current_price = get_current_price(ticker, live)
        except Exception as error:
            print(f"{ticker}: {error}")
            continue

        shares = position["shares"]
        buy_price = position["buy_price"]
        invested = buy_price * shares
        market_value = current_price * shares
        gain_loss = market_value - invested
        return_percent = gain_loss / invested * 100

        results.append({
            "ticker": ticker,
            "shares": shares,
            "buy_price": buy_price,
            "current_price": current_price,
            "invested": invested,
            "market_value": market_value,
            "gain_loss": gain_loss,
            "return_percent": return_percent,
        })

        print(
            f"{ticker:<10}{shares:>10.2f}{buy_price:>13.2f}"
            f"{current_price:>13.2f}{gain_loss:>14.2f}"
            f"{return_percent:>10.2f}%"
        )

    total_invested = sum(r["invested"] for r in results)
    total_market_value = sum(r["market_value"] for r in results)
    total_gain_loss = total_market_value - total_invested
    overall_return = (
        total_gain_loss / total_invested * 100 if total_invested else 0
    )

    print("-" * TABLE_WIDTH)
    print(f"Total invested:       {total_invested:,.2f}")
    print(f"Current market value: {total_market_value:,.2f}")
    print(f"Total gain/loss:      {total_gain_loss:,.2f}")
    print(f"Overall return:       {overall_return:.2f}%")

    return results


def export_csv(results):
    if not results:
        print("\nNo priced holdings to export.")
        return

    write_header = not PORTFOLIO_FILE.exists() or PORTFOLIO_FILE.stat().st_size == 0
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    with PORTFOLIO_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)

        if write_header:
            writer.writeheader()

        writer.writerows({"timestamp": timestamp, **result} for result in results)

    print(f"\nSummary saved to {PORTFOLIO_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate and export stock portfolio performance."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use recent market prices from yfinance.",
    )
    args = parser.parse_args()

    portfolio = collect_portfolio()

    if not portfolio:
        print("No portfolio positions entered.")
        return

    results = calculate_portfolio(portfolio, live=args.live)
    export_csv(results)


if __name__ == "__main__":
    main()