#!/usr/bin/env python3
"""
Stock Market Visualization Startup Script

This script starts the Flask web application for real-time stock market visualization.

To run:
1. Install dependencies: pip install -r requirements.txt
2. Run this script: python run_visualization.py
3. Open http://localhost:5000 in your browser

Features:
- Real-time price chart
- Live order book display
- Trader portfolio tracking
- Interactive trading controls (start/stop/reset)
"""

import os
import sys

def main():
    print("=" * 60)
    print("🚀 Starting Stock Market Visualization Server")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        'market_visualizer.py',
        'StockExchange.py',
        'RandomTraders.py',
        'templates/index.html'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are in the correct location.")
        return
    
    # Check if dependencies are installed
    try:
        import flask
        import flask_socketio
        print("✅ Flask dependencies found")
    except ImportError as e:
        print("❌ Missing dependencies. Please install with:")
        print("   pip install -r requirements.txt")
        print(f"\nError: {e}")
        return
    
    print("✅ All requirements satisfied")
    print("\n📊 Features available:")
    print("   - Real-time price chart")
    print("   - Live order book")
    print("   - Trader portfolios")
    print("   - Interactive controls")
    
    print(f"\n🌐 Server will start at: http://localhost:5000")
    print("\n🔧 Controls:")
    print("   - Start Trading: Begin random trading simulation")
    print("   - Stop Trading: Pause the simulation")
    print("   - Reset Market: Reset to initial state")
    
    print("\n" + "=" * 60)
    print("Starting server... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    # Import and run the Flask app
    try:
        from market_visualizer import app, socketio, initialize_market
        initialize_market()
        socketio.run(app, debug=False,)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == '__main__':
    main()