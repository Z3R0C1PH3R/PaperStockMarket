# Market Simulation Configuration
# Adjust these parameters to customize the trading simulation

# Trading Simulation Settings
SIMULATION_SETTINGS = {
    # Number of random traders in the simulation
    "num_traders": 1000,
    
    # Initial balance for each trader (in dollars)
    "initial_trader_balance": 20000,
    
    # Orders placed per second during active trading
    "orders_per_second": 100,
    
    # Time between market data updates (in seconds)
    "update_interval": 0.2,
}

# Stock Market Settings
STOCK_SETTINGS = {
    # Default stock for simulation
    "default_stock_id": "TECH",
    
    # IPO settings
    "ipo_shares": 100000,
    "ipo_price": 100,
    
    # Price variation percentage for limit orders (±%)
    "price_variation_percent": 1,
    
    # Maximum quantity per order
    "max_order_quantity": 100,
    
    # Number of traders that get initial stock holdings
    "initial_stock_holders": 1000,
    
    # Initial stock quantity given to each holder
    "initial_stock_quantity": 100,
}

# Candlestick Chart Settings
CHART_SETTINGS = {
    # Interval for each candlestick (in seconds)
    "candlestick_interval": 1,
    
    # Maximum number of candles to keep in memory
    "max_candles": 50,
    
    # Chart colors
    "bullish_color": "#4CAF50",    # Green for up moves
    "bearish_color": "#f44336",    # Red for down moves
}

# Web Server Settings
SERVER_SETTINGS = {
    # Flask server host
    "host": "0.0.0.0",
    
    # Flask server port
    "port": 5000,
    
    # Enable debug mode
    "debug": True,
    
    # WebSocket async mode
    "async_mode": "threading",
}

# Order Book Display Settings
DISPLAY_SETTINGS = {
    # Maximum orders to show in order book
    "max_orders_displayed": 18,
    
    # Update frequency for market data (milliseconds) - for future auto-refresh features
    "frontend_update_rate": 1000,
    
    # Number of decimal places for prices
    "price_decimals": 2,
    
    # Maximum price history points to keep
    "max_price_history": 100,
}

# Advanced Trading Settings
ADVANCED_SETTINGS = {
    # Probability of placing buy vs sell orders (0.5 = 50/50)
    "buy_probability": 0.5,
    
    # Probability of placing limit vs market orders (1.0 = 100% limit orders)
    "limit_order_probability": 0.7,
    
    # Minimum balance required to place buy orders
    "min_balance_for_trading": 0,
    
    # Minimum stock quantity required to place sell orders
    "min_stock_for_selling": 0,
}