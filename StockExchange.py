from sortedcontainers import SortedDict

class StockExchange:
    """A simple order book for multiple stock trading simulation."""
    
    def __init__(self):
        self.stocks = {} # contains SortedDicts bids and asks for each stock
        self.users_balances = {} # contains money in bank of each user_id
        self.users_portfolios = {} # contains dict of stocks in portfolio of each user_id
        self.last_traded_prices = {} # track last traded price for each stock
        self.add_user(0) # The market user_id

    def ipo_stock(self, stock_id, quantity, price=100):
        """Initial Public Offering for a stock. Sets the initial price."""
        if stock_id in self.stocks:
            raise ValueError("Stock already exists.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        # Create empty order book
        self.stocks[stock_id] = {
            "bids": SortedDict(),
            "asks": SortedDict()
        }
        
        # Initialize market user portfolio if it doesn't exist
        if stock_id not in self.users_portfolios[0]:
            self.users_portfolios[0][stock_id] = 0
        self.users_portfolios[0][stock_id] += quantity  # Market user gets the stock directly
        self.last_traded_prices[stock_id] = price  # Set initial price


    def add_user(self, user_id, initial_balance=0):
        """Add a user with an initial balance."""
        if user_id in self.users_balances:
            raise ValueError("User already exists.")
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        
        self.users_balances[user_id] = initial_balance
        self.users_portfolios[user_id] = {}
    

    def get_user_balance(self, user_id):
        """Get the balance of a user."""
        if user_id not in self.users_balances:
            raise ValueError("User does not exist.")
        return self.users_balances[user_id]
    

    def get_user_portfolio(self, user_id):
        """Get the portfolio of a user."""
        if user_id not in self.users_portfolios:
            raise ValueError("User does not exist.")
        return self.users_portfolios[user_id]
    
    def get_stock_orders(self, stock_id):
        """Get the current orders for a stock."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        return self.stocks[stock_id]

    def get_last_traded_price(self, stock_id):
        """Get the last traded price for a stock."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        return self.last_traded_prices.get(stock_id, None)

    def get_stock_price(self, stock_id):
        """Get the current price of a stock based on the best ask."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        stock = self.stocks[stock_id]
        
        # If a trade has occurred, use the last traded price
        if stock_id in self.last_traded_prices and self.last_traded_prices[stock_id] is not None:
            return self.last_traded_prices[stock_id]

        # If we have both bids and asks, return the midpoint
        if stock["bids"] and stock["asks"]:
            highest_bid = next(iter(reversed(stock["bids"].keys())))
            lowest_ask = next(iter(stock["asks"].keys()))
            return (highest_bid + lowest_ask) / 2
        
        # If we only have asks, return the lowest ask
        elif stock["asks"]:
            return next(iter(stock["asks"].keys()))
        
        # If we only have bids, return the highest bid
        elif stock["bids"]:
            return next(iter(reversed(stock["bids"].keys())))
        
        # If no orders exist, return None
        else:
            # Fallback to IPO price if no trades or orders exist
            return self.last_traded_prices.get(stock_id, None)

    def get_lowest_ask(self, stock_id):
        """Get the lowest ask price for a stock."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        stock = self.stocks[stock_id]
        if not stock["asks"]:
            return None
        return next(iter(stock["asks"].keys()))

    def get_highest_bid(self, stock_id):
        """Get the highest bid price for a stock."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        stock = self.stocks[stock_id]
        if not stock["bids"]:
            return None
        return next(iter(reversed(stock["bids"].keys())))

    def transfer_stock(self, from_user_id, to_user_id, stock_id, quantity):
        """Transfer stock from one user to another."""
        if from_user_id not in self.users_balances or to_user_id not in self.users_balances:
            raise ValueError("One of the users does not exist.")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        # Check if sender has enough stock
        from_stock_quantity = self.users_portfolios[from_user_id].get(stock_id, 0)
        if from_stock_quantity < quantity:
            raise ValueError(f"Not enough stock to transfer. Has {from_stock_quantity}, needs {quantity}")
        
        # Perform the transfer
        self.users_portfolios[from_user_id][stock_id] -= quantity
        
        # Clean up zero quantities
        if self.users_portfolios[from_user_id][stock_id] == 0:
            del self.users_portfolios[from_user_id][stock_id]
        
        if stock_id not in self.users_portfolios[to_user_id]:
            self.users_portfolios[to_user_id][stock_id] = 0
        self.users_portfolios[to_user_id][stock_id] += quantity

    def transfer_money(self, from_user_id, to_user_id, amount):
        """Transfer money from one user to another."""
        if from_user_id not in self.users_balances or to_user_id not in self.users_balances:
            raise ValueError("One of the users does not exist.")
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        
        if self.users_balances[from_user_id] < amount:
            raise ValueError(f"Not enough balance to transfer. Has {self.users_balances[from_user_id]}, needs {amount}")
        
        # Perform the transfer
        self.users_balances[from_user_id] -= amount
        self.users_balances[to_user_id] += amount

    def place_order(self, stock_id, user_id, bid_or_ask, order_type, quantity, order_price=None):
        """Place an order for a user. order_type can be 'market' or 'limit'."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        
        stock = self.stocks[stock_id]

        if user_id not in self.users_balances:
            raise ValueError("User does not exist.")
        
        if quantity is None or quantity <= 0:
            raise ValueError("Quantity must be specified and greater than zero.")

        if bid_or_ask not in ["bid", "ask"]:
            raise ValueError("bid_or_ask must be 'bid' or 'ask'.")
        
        if order_type not in ["market", "limit"]:
            raise ValueError("order_type must be 'market' or 'limit'.")
        
        if order_type == "limit" and order_price is None:
            raise ValueError("For limit orders, price must be specified.")

        # Validate user has sufficient resources BEFORE any order processing
        if bid_or_ask == "ask":
            # Check if user has enough stock to sell
            user_stock_quantity = self.users_portfolios[user_id].get(stock_id, 0)
            if user_stock_quantity < quantity:
                raise ValueError(f"Not enough stock to sell. Has {user_stock_quantity}, needs {quantity}")
        
        elif bid_or_ask == "bid":
            # For market orders, check against lowest ask price
            # For limit orders, check against the limit price
            price_to_check = order_price if order_type == "limit" else self.get_lowest_ask(stock_id)
            if price_to_check is not None:
                required_balance = price_to_check * quantity
                if self.users_balances[user_id] < required_balance:
                    raise ValueError(f"Not enough balance to buy. Has {self.users_balances[user_id]}, needs {required_balance}")

        if bid_or_ask == "bid":
            bought_quantity = 0
            total_spent = 0
            remaining_quantity = quantity
            
            # Try to match with existing asks first
            for price in list(stock["asks"].keys()):
                if order_type == "limit" and price > order_price:
                    break
                if remaining_quantity <= 0:
                    break

                orders_at_price = stock["asks"][price]
                
                # Process orders at this price level
                orders_to_remove = []
                for i, (seller_id, seller_quantity) in enumerate(orders_at_price):
                    if remaining_quantity <= 0:
                        break
                    
                    trade_quantity = min(remaining_quantity, seller_quantity)
                    cost = price * trade_quantity
                    
                    # Double-check resources are still available
                    if (self.users_balances[user_id] < cost or 
                        self.users_portfolios[seller_id].get(stock_id, 0) < trade_quantity):
                        continue  # Skip this order if resources not available
                    
                    # Execute the trade
                    self.transfer_money(user_id, seller_id, cost)
                    self.transfer_stock(seller_id, user_id, stock_id, trade_quantity)
                    
                    self.last_traded_prices[stock_id] = price
                    
                    remaining_quantity -= trade_quantity
                    bought_quantity += trade_quantity
                    total_spent += cost
                    
                    if trade_quantity == seller_quantity:
                        # Mark order for removal
                        orders_to_remove.append(i)
                    else:
                        # Update the remaining quantity
                        orders_at_price[i] = (seller_id, seller_quantity - trade_quantity)
                
                # Remove completed orders (in reverse order to maintain indices)
                for i in reversed(orders_to_remove):
                    orders_at_price.pop(i)
                    
                if not orders_at_price:
                    # Remove price level if all orders are gone
                    stock["asks"].pop(price)

            # If there's remaining quantity and it's a limit order, add to order book
            if order_type == "limit" and remaining_quantity > 0:
                # Re-validate the user still has enough money for the limit order
                required_balance = order_price * remaining_quantity
                if self.users_balances[user_id] >= required_balance:
                    stock["bids"].setdefault(order_price, []).append((user_id, remaining_quantity))
                    
            return bought_quantity, total_spent
        
        elif bid_or_ask == "ask":
            sold_quantity = 0
            total_earned = 0
            remaining_quantity = quantity
            
            # Try to match with existing bids first
            for price in reversed(list(stock["bids"].keys())):
                if order_type == "limit" and price < order_price:
                    break
                if remaining_quantity <= 0:
                    break

                orders_at_price = stock["bids"][price]
                
                # Process orders at this price level
                orders_to_remove = []
                for i, (buyer_id, buyer_quantity) in enumerate(orders_at_price):
                    if remaining_quantity <= 0:
                        break
                    
                    trade_quantity = min(remaining_quantity, buyer_quantity)
                    cost = price * trade_quantity
                    
                    # Double-check resources are still available
                    if (self.users_balances[buyer_id] < cost or 
                        self.users_portfolios[user_id].get(stock_id, 0) < trade_quantity):
                        continue  # Skip this order if resources not available
                    
                    # Execute the trade
                    self.transfer_money(buyer_id, user_id, cost)
                    self.transfer_stock(user_id, buyer_id, stock_id, trade_quantity)
                    
                    self.last_traded_prices[stock_id] = price
                    
                    remaining_quantity -= trade_quantity
                    sold_quantity += trade_quantity
                    total_earned += cost
                    
                    if trade_quantity == buyer_quantity:
                        # Mark order for removal
                        orders_to_remove.append(i)
                    else:
                        # Update the remaining quantity
                        orders_at_price[i] = (buyer_id, buyer_quantity - trade_quantity)
                
                # Remove completed orders (in reverse order to maintain indices)
                for i in reversed(orders_to_remove):
                    orders_at_price.pop(i)
                    
                if not orders_at_price:
                    # Remove price level if all orders are gone
                    stock["bids"].pop(price)

            # If there's remaining quantity and it's a limit order, add to order book
            if order_type == "limit" and remaining_quantity > 0:
                # Re-validate the user still has enough stock for the limit order
                if self.users_portfolios[user_id].get(stock_id, 0) >= remaining_quantity:
                    stock["asks"].setdefault(order_price, []).append((user_id, remaining_quantity))
                    
            return sold_quantity, total_earned
        
    def cancel_order(self, stock_id, user_id, bid_or_ask, order_price):
        """Cancel an order for a user."""
        if stock_id not in self.stocks:
            raise ValueError("Stock does not exist.")
        
        stock = self.stocks[stock_id]

        if user_id not in self.users_balances:
            raise ValueError("User does not exist.")
        
        if bid_or_ask not in ["bid", "ask"]:
            raise ValueError("bid_or_ask must be 'bid' or 'ask'.")
        
        if order_price not in stock[bid_or_ask+"s"]:
            raise ValueError("No such order exists.")
        
        orders = stock[bid_or_ask+"s"][order_price]
        for i, (user_id2, quantity) in enumerate(orders):
            if user_id2 == user_id:
                orders.pop(i)
                return quantity
            
        raise ValueError("No order found for this user at the specified price.")
    
    def print_market_summary(self):
        """Print a summary of the market."""
        print("Market Summary:")
        for stock_id, stock in self.stocks.items():
            print(f"Stock: {stock_id}")
            for price, orders in reversed(stock["asks"].items()):
                print(f"  Ask at {price}, Orders: {orders}")
            print("---")
            for price, orders in reversed(stock["bids"].items()):
                print(f"  Bid at {price}, Orders: {orders}")
        print()
        for user_id, balance in self.users_balances.items():
            print(f"User {user_id}: Balance = {balance}")
        print()
        for user_id, portfolio in self.users_portfolios.items():
            print(f"User {user_id}: Portfolio = {portfolio}")
        print()

    def verify_conservation(self):
        """Verify that money and stocks are conserved in the system."""
        total_money = sum(self.users_balances.values())
        stock_totals = {}
        
        for user_id, portfolio in self.users_portfolios.items():
            for stock_id, quantity in portfolio.items():
                if stock_id not in stock_totals:
                    stock_totals[stock_id] = 0
                stock_totals[stock_id] += quantity
        
        # Add stocks in open orders
        for stock_id, stock in self.stocks.items():
            for price, orders in stock["asks"].items():
                for user_id, quantity in orders:
                    if stock_id not in stock_totals:
                        stock_totals[stock_id] = 0
                    stock_totals[stock_id] += quantity
        
        print(f"Total money in system: ${total_money:.2f}")
        for stock_id, total in stock_totals.items():
            print(f"Total {stock_id} shares: {total}")
        
        return total_money, stock_totals
    
    def clean_invalid_orders(self, stock_id):
        """Remove orders where users no longer have sufficient resources."""
        if stock_id not in self.stocks:
            return
        
        stock = self.stocks[stock_id]
        
        # Clean invalid bids (users without enough money)
        for price in list(stock["bids"].keys()):
            orders = stock["bids"][price]
            valid_orders = []
            
            for user_id, quantity in orders:
                required_balance = price * quantity
                if self.users_balances.get(user_id, 0) >= required_balance:
                    valid_orders.append((user_id, quantity))
            
            if valid_orders:
                stock["bids"][price] = valid_orders
            else:
                del stock["bids"][price]
        
        # Clean invalid asks (users without enough stock)
        for price in list(stock["asks"].keys()):
            orders = stock["asks"][price]
            valid_orders = []
            
            for user_id, quantity in orders:
                user_stock = self.users_portfolios.get(user_id, {}).get(stock_id, 0)
                if user_stock >= quantity:
                    valid_orders.append((user_id, quantity))
            
            if valid_orders:
                stock["asks"][price] = valid_orders
            else:
                del stock["asks"][price]