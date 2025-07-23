# Configuration Guide

This file explains how to customize the stock market simulation using the `config.py` file.

## Quick Start

All simulation parameters are now centralized in `config.py`. Simply edit the values and restart the application.

## Configuration Sections

### 1. SIMULATION_SETTINGS
Controls the basic simulation behavior:

- **num_traders**: Number of random traders (default: 8)
- **initial_trader_balance**: Starting money for each trader (default: $50,000)
- **orders_per_second**: Trading frequency (default: 2 orders/second)
- **update_interval**: How often market data updates (default: 1 second)

### 2. STOCK_SETTINGS
Controls the stock and IPO configuration:

- **default_stock_id**: Stock symbol (default: "TECH")
- **ipo_shares**: Total shares issued (default: 10,000)
- **ipo_price**: Initial stock price (default: $100)
- **price_variation_percent**: Order price range ±% (default: 10%)
- **max_order_quantity**: Maximum shares per order (default: 10)

### 3. CHART_SETTINGS
Controls the candlestick chart display:

- **candlestick_interval**: Seconds per candle (default: 10)
- **max_candles**: Maximum candles displayed (default: 50)
- **chart_height**: Chart height in pixels (default: 300)
- **bullish_color**: Green color for up moves (default: "#4CAF50")
- **bearish_color**: Red color for down moves (default: "#f44336")

### 4. SERVER_SETTINGS
Controls the web server:

- **host**: Server host (default: "0.0.0.0")
- **port**: Server port (default: 5000)
- **debug**: Enable debug mode (default: True)

### 5. ADVANCED_SETTINGS
Fine-tune trading behavior:

- **buy_probability**: Chance of buy vs sell (default: 0.5 = 50/50)
- **limit_order_probability**: Chance of limit vs market orders (default: 1.0 = 100% limit)
- **min_balance_for_trading**: Minimum cash to trade (default: $100)

## Common Customizations

### Make Trading More Active
```python
SIMULATION_SETTINGS = {
    "num_traders": 15,           # More traders
    "orders_per_second": 5,      # More frequent orders
    "update_interval": 0.5,      # Faster updates
}
```

### Create Faster Candles
```python
CHART_SETTINGS = {
    "candlestick_interval": 5,   # 5-second candles
    "max_candles": 100,          # More history
}
```

### Increase Price Volatility
```python
STOCK_SETTINGS = {
    "price_variation_percent": 20,  # ±20% price range
    "max_order_quantity": 50,       # Larger orders
}
```

### Create Bullish Market
```python
ADVANCED_SETTINGS = {
    "buy_probability": 0.7,      # 70% buy orders
}
```

## Restart Required

After editing `config.py`, restart the application:
```bash
python market_visualizer.py
```

The changes will take effect immediately.