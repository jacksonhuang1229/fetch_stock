import yfinance as yf
from datetime import datetime

def fetch_us_market():
    symbols = {
        "道瓊": "^DJI",
        "標普500": "^GSPC",
        "那斯達克": "^IXIC",
        "費半": "^SOX"
    }

    for name, symbol in symbols.items():
        data = yf.Ticker(symbol).history(period="1d")
        close = data["Close"].iloc[-1]
        volume = data["Volume"].iloc[-1]
        prev_close = data["Close"].iloc[-2]
        change = close - prev_close
        percent = (change / prev_close) * 100
        print(f"{datetime.now()} {name}: {close:.2f}, 漲跌 {change:.2f} ({percent:.2f}%), 成交量 {volume}")

if __name__ == "__main__":
    fetch_us_market()
