import time
import urllib.request
import re
import finviz
from finviz.screener import Screener
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class FinvizClient:
    def __init__(self, delay_seconds: float = 3.0):
        """
        Initializes the Finviz API client using the mariostoev/finviz library.
        Includes a rate limiter wrapper to prevent IP bans.

        Args:
            delay_seconds (float): Minimum seconds to wait between requests.
        """
        self.delay_seconds = delay_seconds
        self._last_request_time = 0.0

    def _enforce_rate_limit(self):
        """Blocks execution until the required delay time has passed since the last request."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            logger.debug(f"Finviz rate limit active. Pausing for {sleep_time:.2f}s...")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def get_stock_fundamentals(self, symbol: str) -> dict:
        """
        Fetches the complete fundamental data table (P/E, Debt/Eq, ROE, etc.) for a ticker.
        """
        self._enforce_rate_limit()
        logger.info(f"Fetching fundamental data for {symbol} using finviz library...")

        try:
            # The finviz library returns a dictionary of 90+ data points automatically
            data = finviz.get_stock(symbol.upper())
            logger.info(
                f"Successfully fetched {len(data)} fundamental metrics for {symbol}."
            )
            return data

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {e}")
            return {}

    def get_screener_tickers(self, filters: list) -> list:
        """
        Navigates Finviz screener pages and extracts all matching tickers.
        Manually handles pagination to enforce rate limits between page loads.

        Args:
            filters (list): List of Finviz filter codes.
                            (e.g., ['cap_midover', 'fa_pe_u20', 'fa_debteq_u1'])
        """
        logger.info(f"Running Finviz screener with filters: {filters}...")

        filter_str = ",".join(filters)
        base_url = f"https://finviz.com/screener.ashx?v=111&f={filter_str}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        tickers = []
        page_start = 1

        try:
            while True:
                logger.info(
                    f"Fetching screener results {page_start} to {page_start + 19}... (Total found so far: {len(tickers)})"
                )

                # Enforce the delay BEFORE fetching every single page!
                self._enforce_rate_limit()

                url = f"{base_url}&r={page_start}"
                req = urllib.request.Request(url, headers=headers)

                with urllib.request.urlopen(req) as response:
                    html = response.read().decode("utf-8")

                # Extract tickers using regex on the quote link instead of CSS class
                page_tickers = re.findall(r"quote\.ashx\?t=([A-Z\-]+)", html)

                if not page_tickers:
                    break

                # Maintain order and remove duplicates
                seen = set()
                unique_tickers = [
                    x for x in page_tickers if not (x in seen or seen.add(x))
                ]

                tickers.extend(unique_tickers)

                # Finviz returns 20 results per page by default
                if len(unique_tickers) < 20:
                    break

                page_start += 20

            logger.info(
                f"Screener execution complete. Found {len(tickers)} total matching tickers."
            )
            return tickers

        except Exception as e:
            logger.error(f"Error executing Finviz screener: {e}")
            return tickers  # Return whatever we successfully grabbed before the error
