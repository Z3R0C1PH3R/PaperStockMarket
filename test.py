from StockExchange import StockExchange
ob = StockExchange()
ob.add_user("nigga", 10000)
ob.add_user("niggi", 10000)
ob.ipo_stock("NGGR", 100, 10)

print(ob.place_order("NGGR", "nigga", "bid", "market", 10))
print(ob.place_order("NGGR", "nigga", "ask", "limit", 10, 11))
print(ob.place_order("NGGR", "niggi", "bid", "limit", 10, 9))
print(ob.place_order("NGGR", "niggi", "bid", "limit", 10, 8))
print(ob.place_order("NGGR", "nigga", "ask", "market", 10))

print("price", ob.get_stock_price("NGGR"))

ob.print_market_summary()