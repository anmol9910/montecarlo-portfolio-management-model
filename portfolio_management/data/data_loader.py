import pandas as pd
import yfinance as yf
from typing import List, Union


class DataLoader:
    def load_data(
        self,
        tickers: List[str],
        start_date: Union[str, pd.Timestamp],
        end_date: Union[str, pd.Timestamp]
    ) -> pd.DataFrame:
        """
        Load closing prices for the given tickers and date range.
        Primary source: Yahoo Finance (yfinance).
        Fallback: Stooq (reliable, no VPN required).
        """

        # Yahoo format fix (e.g., BRK.B → BRK-B)
        tickers = [t.replace(".", "-") for t in tickers]

        stock_data = {}

        # Try Yahoo Finance first
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(start=start_date, end=end_date)

                if not hist.empty:
                    stock_data[ticker] = hist["Close"]
                else:
                    print(f"⚠️ No data found on Yahoo for {ticker}")

            except Exception as e:
                print(f"❌ Yahoo error for {ticker}: {e}")

        # If Yahoo returned nothing → fallback to Stooq
        if not stock_data:
            print("⚠️ Yahoo failed. Falling back to Stooq...")
            for ticker in tickers:
                try:
                    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
                    df = pd.read_csv(url)
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.set_index("Date")
                    stock_data[ticker] = df["Close"].loc[start_date:end_date]
                except Exception as e:
                    print(f"❌ Stooq error for {ticker}: {e}")

        if not stock_data:
            print("⚠️ No valid data returned from Yahoo or Stooq.")
            return pd.DataFrame()

        return pd.DataFrame(stock_data)


if __name__ == "__main__":
    loader = DataLoader()
    tickers = ["AAPL", "MSFT", "GOOG"]
    start = "2020-01-01"
    end = "2023-01-01"

    df = loader.load_data(tickers, start, end)
    print(df.head())
