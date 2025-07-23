from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
import random
from datetime import datetime
from StockExchange import StockExchange
from RandomTraders import RandomTraders
from config import SIMULATION_SETTINGS, STOCK_SETTINGS, CHART_SETTINGS, SERVER_SETTINGS, DISPLAY_SETTINGS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock_market_viz'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=SERVER_SETTINGS["async_mode"])

# Global variables for the exchange and traders
exchange = None
traders = None
price_history = []
candlestick_data = []
current_candle = None
trading_active = False

def initialize_market():
    """Initialize the stock exchange and traders."""
    global exchange, traders, price_history, candlestick_data, current_candle
    
    try:
        print("Initializing market...")
        
        # Reset data
        price_history = []
        candlestick_data = []
        current_candle = None
        
        # Create exchange
        exchange = StockExchange()
        print("Exchange created")
        
        # IPO the stock
        stock_id = STOCK_SETTINGS["default_stock_id"]
        ipo_shares = STOCK_SETTINGS["ipo_shares"]
        ipo_price = STOCK_SETTINGS["ipo_price"]
        exchange.ipo_stock(stock_id, ipo_shares, ipo_price)
        print(f"{stock_id} stock IPO completed: {ipo_shares:,} shares at ${ipo_price}")
        
        # Create random traders
        num_traders = SIMULATION_SETTINGS["num_traders"]
        initial_balance = SIMULATION_SETTINGS["initial_trader_balance"]
        traders = RandomTraders(exchange, stock_id, num_traders, initial_balance)
        print(f"Created {len(traders.trader_ids)} traders with ${initial_balance:,} each")
        
        # Give some traders initial stock holdings using market orders
        initial_holders = STOCK_SETTINGS["initial_stock_holders"]
        initial_quantity = STOCK_SETTINGS["initial_stock_quantity"]
        
        # First, market user (id=0) needs to place ask orders to sell stock to traders
        total_to_distribute = min(initial_holders, num_traders) * initial_quantity
        if total_to_distribute > 0:
            # Market user places ask order at IPO price
            try:
                exchange.place_order(stock_id, 0, "ask", "limit", total_to_distribute, ipo_price)
                print(f"Market user placed ask order for {total_to_distribute} shares at ${ipo_price}")
            except Exception as ask_error:
                print(f"Error placing market ask order: {ask_error}")
        
        # Now traders place market buy orders to get their initial holdings
        for trader_id in range(1, min(initial_holders + 1, num_traders + 1)):
            try:
                # Trader places market buy order
                bought, spent = exchange.place_order(stock_id, trader_id, "bid", "market", initial_quantity)
                if bought > 0:
                    print(f"Trader {trader_id} bought {bought} {stock_id} shares for ${spent:.2f}")
                else:
                    print(f"Trader {trader_id} failed to buy initial stock")
            except Exception as buy_error:
                print(f"Error with trader {trader_id} initial purchase: {buy_error}")
        
        print("Market initialization completed successfully")
        
        # Test market data retrieval
        test_data = get_market_data()
        if test_data:
            print("Market data retrieval test: SUCCESS")
        else:
            print("Market data retrieval test: FAILED")
            
    except Exception as e:
        print(f"Error initializing market: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

def update_candlestick_data(price):
    """Update candlestick data with new price."""
    global current_candle, candlestick_data
    
    current_time = datetime.now()
    # Use configurable interval for candles
    interval_seconds = CHART_SETTINGS["candlestick_interval"]
    current_interval = current_time.replace(second=(current_time.second // interval_seconds) * interval_seconds, microsecond=0)
    
    if current_candle is None or current_candle['time'] != current_interval.isoformat():
        # Start a new candle
        if current_candle is not None:
            candlestick_data.append(current_candle)
        
        # Get the last traded price as the opening price for new candle
        last_price = exchange.get_last_traded_price(STOCK_SETTINGS["default_stock_id"])
        opening_price = last_price if last_price is not None else price
        
        current_candle = {
            'time': current_interval.isoformat(),
            'open': opening_price,
            'high': price,
            'low': price,
            'close': price,
            'timestamp': current_interval.isoformat()
        }
        print(f"📊 New candle started: Open=${opening_price:.2f}, Price=${price:.2f}")
    else:
        # Update current candle
        current_candle['high'] = max(current_candle['high'], price)
        current_candle['low'] = min(current_candle['low'], price)
        current_candle['close'] = price
    
    # Let candlestick_data grow to preserve history for client-side panning/zooming

def get_market_data(include_full_history=True):
    """Get current market data for visualization."""
    if not exchange:
        print("Error: Exchange not initialized")
        return None
    
    if not traders:
        print("Error: Traders not initialized")
        return None
    
    try:
        current_price = exchange.get_stock_price(STOCK_SETTINGS["default_stock_id"])
        lowest_ask = exchange.get_lowest_ask(STOCK_SETTINGS["default_stock_id"])
        highest_bid = exchange.get_highest_bid(STOCK_SETTINGS["default_stock_id"])
        stock_orders = exchange.get_stock_orders(STOCK_SETTINGS["default_stock_id"])
        
        # Get order book data
        bids = []
        asks = []
        
        if "bids" in stock_orders:
            for price, orders in stock_orders["bids"].items():
                total_quantity = sum(qty for _, qty in orders)
                bids.append({"price": float(price), "quantity": total_quantity})
        
        if "asks" in stock_orders:
            for price, orders in stock_orders["asks"].items():
                total_quantity = sum(qty for _, qty in orders)
                asks.append({"price": float(price), "quantity": total_quantity})
        
        # Get user balances and portfolios
        users_data = []
        if hasattr(traders, 'trader_ids') and traders.trader_ids:
            for user_id in traders.trader_ids:
                try:
                    balance = exchange.get_user_balance(user_id)
                    portfolio = exchange.get_user_portfolio(user_id)
                    stock_quantity = portfolio.get("TECH", 0)
                    total_value = balance + (stock_quantity * (current_price or 100))
                    
                    users_data.append({
                        "user_id": user_id,
                        "balance": round(float(balance), 2),
                        "stock_quantity": int(stock_quantity),
                        "total_value": round(float(total_value), 2)
                    })
                except Exception as user_error:
                    print(f"Error getting data for user {user_id}: {user_error}")
                    continue
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "current_price": round(float(current_price), DISPLAY_SETTINGS["price_decimals"]) if current_price else None,
            "lowest_ask": round(float(lowest_ask), DISPLAY_SETTINGS["price_decimals"]) if lowest_ask else None,
            "highest_bid": round(float(highest_bid), DISPLAY_SETTINGS["price_decimals"]) if highest_bid else None,
            "spread": round(float(lowest_ask - highest_bid), DISPLAY_SETTINGS["price_decimals"]) if (lowest_ask and highest_bid) else None,
            "bids": sorted(bids, key=lambda x: x["price"], reverse=True)[:DISPLAY_SETTINGS["max_orders_displayed"]],
            "asks": sorted(asks, key=lambda x: x["price"])[:DISPLAY_SETTINGS["max_orders_displayed"]],
            "users": users_data,
        }

        if include_full_history:
            data["candlestick_data"] = candlestick_data + ([current_candle] if current_candle else [])
        else:
            data["latest_candle"] = current_candle

        return data
    except Exception as e:
        print(f"Error getting market data: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def trading_loop():
    """Background trading loop that places random orders."""
    global trading_active, price_history
    
    print("Trading loop started")
    
    while trading_active:
        try:
            if not exchange or not traders:
                print("Exchange or traders not initialized, stopping trading loop")
                break
                
            # Place some random orders
            for _ in range(SIMULATION_SETTINGS["orders_per_second"]):
                try:
                    trader_id = random.choice(traders.trader_ids)
                    traders.place_random_order(trader_id)
                except Exception as order_error:
                    print(f"Error placing order: {order_error}")
                    continue
            
            # Clean up invalid orders before market data update
            exchange.clean_invalid_orders(STOCK_SETTINGS["default_stock_id"])
            
            # Get current market price and update the candle
            current_price = exchange.get_stock_price(STOCK_SETTINGS["default_stock_id"])
            if current_price:
                update_candlestick_data(current_price)
            
            # Get market data without the full history for the socket emission
            market_data_for_emit = get_market_data(include_full_history=False)

            if market_data_for_emit:
                # Emit data to all connected clients
                try:
                    socketio.emit('market_update', {
                        "market_data": market_data_for_emit,
                    })
                except Exception as emit_error:
                    print(f"Error emitting data: {emit_error}")
            
            time.sleep(SIMULATION_SETTINGS["update_interval"])  # Configurable update interval
            
        except Exception as e:
            print(f"Error in trading loop: {type(e).__name__}: {str(e)}")
            time.sleep(1)
    
    print("Trading loop stopped")

@app.route('/')
def index():
    """Main page with the market visualization."""
    return render_template('index.html')

@app.route('/api/market_data')
def api_market_data():
    """API endpoint for current market data."""
    market_data = get_market_data(include_full_history=True)
    return jsonify({
        "market_data": market_data,
    })

@app.route('/api/config')
def api_config():
    """API endpoint for configuration data."""
    return jsonify({
        "chart_settings": CHART_SETTINGS,
        "display_settings": DISPLAY_SETTINGS,
        "simulation_settings": SIMULATION_SETTINGS
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('trading_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('start_trading')
def handle_start_trading():
    """Start the trading simulation."""
    global trading_active
    
    if not trading_active:
        trading_active = True
        # Start trading in a separate thread
        trading_thread = threading.Thread(target=trading_loop)
        trading_thread.daemon = True
        trading_thread.start()
        emit('trading_status', {'status': 'started'})

@socketio.on('stop_trading')
def handle_stop_trading():
    """Stop the trading simulation."""
    global trading_active
    trading_active = False
    emit('trading_status', {'status': 'stopped'})

@socketio.on('reset_market')
def handle_reset_market():
    """Reset the market to initial state."""
    global trading_active, price_history, candlestick_data, current_candle
    trading_active = False
    price_history = []
    candlestick_data = []
    current_candle = None
    initialize_market()
    emit('trading_status', {'status': 'reset'})

if __name__ == '__main__':
    # Initialize the market
    initialize_market()
    
    # Create templates directory if it doesn't exist
    import os
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Stock Market Visualization Server...")
    print("Open http://localhost:5000 in your browser")
    
    socketio.run(app, debug=SERVER_SETTINGS["debug"], host=SERVER_SETTINGS["host"], port=SERVER_SETTINGS["port"], allow_unsafe_werkzeug=True)