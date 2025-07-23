import random
import time
from StockExchange import StockExchange
from config import STOCK_SETTINGS, ADVANCED_SETTINGS

class RandomTraders:
    """Simulates random traders placing orders on a stock exchange."""
    
    def __init__(self, exchange, stock_id, num_traders=10, initial_balance=10000):
        self.exchange = exchange
        self.stock_id = stock_id
        self.num_traders = num_traders
        self.trader_ids = []
        
        # Create traders with initial balances
        for i in range(1, num_traders + 1):
            self.exchange.add_user(i, initial_balance)
            self.trader_ids.append(i)
    
    def get_random_price_around_market(self, base_price, percentage=None):
        """Generate a random price within percentage of base price."""
        if percentage is None:
            percentage = STOCK_SETTINGS["price_variation_percent"]
            
        if base_price is None:
            return random.uniform(90, 110)  # Default range if no market price
        
        variation = base_price * (percentage / 100)
        return random.uniform(base_price - variation, base_price + variation)
    
    def place_random_order(self, trader_id):
        """Place a random order for a trader based on config probabilities."""
        try:
            user_balance = self.exchange.get_user_balance(trader_id)
            user_portfolio = self.exchange.get_user_portfolio(trader_id)
            user_stock_quantity = user_portfolio.get(self.stock_id, 0)
            
            # Determine bid or ask based on config probability
            bid_or_ask = "bid" if random.random() < ADVANCED_SETTINGS["buy_probability"] else "ask"

            # Check if the trader can make the trade
            if bid_or_ask == "bid" and user_balance < ADVANCED_SETTINGS["min_balance_for_trading"]:
                return None  # Not enough money to buy
            if bid_or_ask == "ask" and user_stock_quantity < ADVANCED_SETTINGS["min_stock_for_selling"]:
                return None  # No stock to sell

            # Determine order type (limit or market)
            order_type = "limit" if random.random() < ADVANCED_SETTINGS["limit_order_probability"] else "market"
            
            # Generate a price for limit orders
            current_price = self.exchange.get_stock_price(self.stock_id)
            if current_price is None:
                return None # Can't trade without a price
            
            order_price = None
            if order_type == "limit":
                order_price = self.get_random_price_around_market(current_price)

            # Generate random quantity
            max_qty = STOCK_SETTINGS["max_order_quantity"]
            quantity = 0
            if bid_or_ask == "bid":
                effective_price = order_price if order_type == 'limit' else self.exchange.get_lowest_ask(self.stock_id)
                if not effective_price or effective_price <= 0:
                    return None # Cannot determine price, so cannot buy
                
                max_affordable = int(user_balance / effective_price)
                if max_affordable == 0:
                    return None # Cannot afford any
                quantity = random.randint(1, min(max_qty, max_affordable))
            else: # ask
                if user_stock_quantity == 0:
                    return None # Nothing to sell
                quantity = random.randint(1, min(max_qty, user_stock_quantity))

            if quantity == 0:
                return None

            # Place the order
            result = self.exchange.place_order(
                self.stock_id, trader_id, bid_or_ask, order_type, quantity, order_price
            )
            
            # Print order details
            if result:
                order_details = f"Trader {trader_id}: Placed {order_type} {bid_or_ask} for {quantity} shares"
                if order_type == "limit":
                    order_details += f" @ ${order_price:.2f}"
                
                if bid_or_ask == "bid":
                    bought, spent = result
                    if bought > 0:
                        order_details += f" -> BOUGHT {bought} for ${spent:.2f}"
                else:
                    sold, earned = result
                    if sold > 0:
                        order_details += f" -> SOLD {sold} for ${earned:.2f}"
                
                print(order_details)
                    
            return result
                    
        except Exception as e:
            # Silently handle non-critical errors but log serious validation errors
            if "not enough" in str(e).lower() or "insufficient" in str(e).lower():
                print(f"Warning: Trader {trader_id} validation failed: {e}")
            return None
    
    def simulate_trading_session(self, duration_seconds=60, orders_per_second=2):
        """Simulate a trading session with random orders."""
        print(f"Starting trading simulation for {duration_seconds} seconds...")
        print(f"Target: {orders_per_second} orders per second")
        print("=" * 50)
        
        start_time = time.time()
        order_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Place random orders
            for _ in range(orders_per_second):
                trader_id = random.choice(self.trader_ids)
                self.place_random_order(trader_id)
                order_count += 1
            
            # Print market summary every 10 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                print(f"\n--- After {int(elapsed)} seconds ---")
                current_price = self.exchange.get_stock_price(self.stock_id)
                lowest_ask = self.exchange.get_lowest_ask(self.stock_id)
                highest_bid = self.exchange.get_highest_bid(self.stock_id)
                print(f"Current price: ${current_price:.2f if current_price else 'N/A'}")
                print(f"Lowest ask: ${lowest_ask:.2f if lowest_ask else 'N/A'}")
                print(f"Highest bid: ${highest_bid:.2f if highest_bid else 'N/A'}")
                print(f"Orders placed so far: {order_count}")
                
            time.sleep(1)  # Wait 1 second between rounds
        
        print(f"\nTrading session completed!")
        print(f"Total orders placed: {order_count}")
        print("=" * 50)

if __name__ == "__main__":
    # Create exchange and IPO a stock
    exchange = StockExchange()
    exchange.ipo_stock("TECH", 10000, 100)  # 10,000 shares at $100 each
    
    print("Initial market state:")
    exchange.print_market_summary()
    
    # Create random traders
    traders = RandomTraders(exchange, "TECH", num_traders=5, initial_balance=50000)
    
    # Give some traders initial stock holdings
    for trader_id in [1, 2, 3]:
        exchange.transfer_stock(0, trader_id, "TECH", 100)  # Transfer 100 shares from market to trader
    
    print("After distributing initial stock:")
    exchange.print_market_summary()
    
    # Run a short trading simulation
    traders.simulate_trading_session(duration_seconds=300, orders_per_second=10)
    
    print("\nFinal market state:")
    exchange.print_market_summary()