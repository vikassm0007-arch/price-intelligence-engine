"""
Day 27 — Real-Time Price Trend Analytics & Delta Aggregator Engine
===================================================================
Learn & Practice advanced price intelligence metrics & trend analytics:
- Moving average price calculations (MA-7, MA-30)
- Price volatility scoring (Standard Deviation of price points)
- Competitive Price Index (CPI) & Price Momentum calculations
"""

import math
import sys
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceAnalyticsAggregator:

    def calculate_moving_average(self, prices: List[float]) -> float:
        """Calculates arithmetic mean of price history."""
        if not prices:
            return 0.0
        return round(sum(prices) / len(prices), 2)

    def calculate_volatility_score(self, prices: List[float]) -> float:
        """Calculates standard deviation of price changes to measure volatility."""
        if len(prices) < 2:
            return 0.0
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
        return round(math.sqrt(variance), 2)

    def calculate_competitive_price_index(self, target_price: float, market_benchmark: float) -> float:
        """
        Calculates Competitive Price Index (CPI).
        CPI < 100 ➔ Priced below market average (competitive advantage)
        CPI > 100 ➔ Priced above market average
        """
        if market_benchmark <= 0:
            return 100.0
        return round((target_price / market_benchmark) * 100, 1)

    def calculate_price_momentum(self, prices: List[float]) -> float:
        """Calculates overall percentage momentum between earliest and latest price snapshot."""
        if len(prices) < 2 or prices[0] == 0:
            return 0.0
        return round(((prices[-1] - prices[0]) / prices[0]) * 100, 2)

    def analyze_product_series(self, title: str, price_history: List[float], market_benchmark: float) -> Dict[str, Any]:
        curr_price = price_history[-1] if price_history else 0.0
        ma = self.calculate_moving_average(price_history)
        volatility = self.calculate_volatility_score(price_history)
        cpi = self.calculate_competitive_price_index(curr_price, market_benchmark)
        momentum = self.calculate_price_momentum(price_history)

        return {
            "product_title": title,
            "current_price": curr_price,
            "moving_average_price": ma,
            "volatility_score": volatility,
            "competitive_price_index": cpi,
            "price_momentum_pct": momentum,
            "price_position": "COMPETITIVE" if cpi <= 100.0 else "PREMIUM",
        }


def run_day_27_demo():
    print("[Day 27] Running Real-Time Price Trend Analytics & Delta Aggregator Engine...\n")
    aggregator = PriceAnalyticsAggregator()

    # Price history across 7 scrapes for 'A Light in the Attic'
    history = [65.00, 62.00, 58.50, 55.00, 51.77, 51.77, 49.99]
    market_benchmark_price = 55.00

    metrics = aggregator.analyze_product_series("A Light in the Attic", history, market_benchmark_price)

    print("📊 Price Intelligence Trend Metrics:")
    for key, val in metrics.items():
        print(f"  • {key.replace('_', ' ').title()}: {val}")


if __name__ == "__main__":
    run_day_27_demo()
