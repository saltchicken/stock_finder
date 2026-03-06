from finviz_api import FinvizClient


def main():
    # Initialize your client
    client = FinvizClient()

    filters = ["sh_avgvol_o1000"]

    # Fetch the tickers
    print("Fetching high volume tickers...")
    high_volume_tickers = client.get_screener_tickers(filters=filters)

    print(f"Found {len(high_volume_tickers)} tickers.")

    if high_volume_tickers:
        print(f"First 10 tickers: {high_volume_tickers[:10]}")  # Print the first 10

        # Save the tickers to a file separated by a newline
        output_file = "tickers.txt"
        with open(output_file, "w", encoding="utf-8") as file:
            for ticker in high_volume_tickers:
                file.write(f"{ticker}\n")

        print(
            f"Successfully saved all {len(high_volume_tickers)} tickers to {output_file}"
        )
    else:
        print("No tickers found to save.")


if __name__ == "__main__":
    main()
