from finviz_api import FinvizClient


def main():
    # Initialize your client
    client = FinvizClient()

    filters = ["sh_avgvol_o1000"]

    # Fetch the tickers
    print("Fetching high volume tickers...")
    high_volume_tickers = client.get_screener_tickers(filters=filters)

    print(f"Found {len(high_volume_tickers)} tickers.")
    print(high_volume_tickers)  # Print the first 10


if __name__ == "__main__":
    main()
