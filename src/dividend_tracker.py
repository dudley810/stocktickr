#!/usr/bin/env python3
"""
Stock Dividend Tracker Module
Provides dividend information for stocks including ex-date, pay date, yield, and amount.
Designed to be integrated with .NET Aspire via cshakes.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any
import sys

class DividendInfo:
    """Data class for dividend information"""
    def __init__(self, symbol: str, dividend_rate: float = 0.0, dividend_yield: float = 0.0,
                 ex_date: str = None, pay_date: str = None, amount_per_share: float = 0.0):
        self.symbol = symbol
        self.dividend_rate = dividend_rate
        self.dividend_yield = dividend_yield
        self.ex_date = ex_date
        self.pay_date = pay_date
        self.amount_per_share = amount_per_share
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'symbol': self.symbol,
            'dividend_rate': self.dividend_rate,
            'dividend_yield': self.dividend_yield,
            'ex_date': self.ex_date,
            'pay_date': self.pay_date,
            'amount_per_share': self.amount_per_share,
            'last_updated': self.last_updated
        }

class StockDividendTracker:
    """Main class for tracking stock dividends"""
    
    def __init__(self):
        # Default dividend-focused stock symbols
        self.dividend_stocks = [
            'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'PEP', 'MCD', 'WMT', 'VZ', 'T',
            'JPM', 'BAC', 'XOM', 'CVX', 'INTC', 'IBM', 'MMM', 'CAT', 'HD', 'MO'
        ]
    
    def get_dividend_info(self, symbol: str) -> DividendInfo:
        """Get dividend information for a single stock symbol"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                return self._create_mock_dividend_info(symbol)
            
            # Extract dividend information
            dividend_rate = info.get('dividendRate', 0.0)
            dividend_yield = info.get('dividendYield', 0.0)
            ex_dividend_date = info.get('exDividendDate')
            
            # Convert timestamp to date string if available
            ex_date_str = None
            if ex_dividend_date:
                try:
                    ex_date_str = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    ex_date_str = str(ex_dividend_date)
            
            # Get recent dividends to find the latest amount per share
            try:
                dividends = stock.dividends
                amount_per_share = dividends.iloc[-1] if not dividends.empty else 0.0
            except:
                amount_per_share = dividend_rate / 4 if dividend_rate > 0 else 0.0  # Quarterly estimate
            
            # Estimate pay date (typically 2-4 weeks after ex-date)
            pay_date_str = None
            if ex_date_str:
                try:
                    ex_date = datetime.strptime(ex_date_str, '%Y-%m-%d')
                    pay_date = ex_date + timedelta(days=21)  # Typical 3-week gap
                    pay_date_str = pay_date.strftime('%Y-%m-%d')
                except:
                    pass
            
            return DividendInfo(
                symbol=symbol,
                dividend_rate=dividend_rate or 0.0,
                dividend_yield=dividend_yield or 0.0,
                ex_date=ex_date_str,
                pay_date=pay_date_str,
                amount_per_share=float(amount_per_share) if amount_per_share else 0.0
            )
            
        except Exception as e:
            print(f"Error fetching dividend info for {symbol}: {e}", file=sys.stderr)
            return self._create_mock_dividend_info(symbol)
    
    def _create_mock_dividend_info(self, symbol: str) -> DividendInfo:
        """Create mock dividend info when real data is unavailable"""
        # Mock data for demonstration - in real scenario this would come from cache or fallback
        mock_data = {
            'AAPL': {'rate': 0.96, 'yield': 0.0044, 'amount': 0.24},
            'MSFT': {'rate': 3.00, 'yield': 0.0067, 'amount': 0.75},
            'JNJ': {'rate': 4.76, 'yield': 0.0301, 'amount': 1.19},
            'PG': {'rate': 3.88, 'yield': 0.0245, 'amount': 0.97},
            'KO': {'rate': 1.94, 'yield': 0.0310, 'amount': 0.485}
        }
        
        data = mock_data.get(symbol, {'rate': 0.0, 'yield': 0.0, 'amount': 0.0})
        
        # Generate mock dates
        today = datetime.now()
        ex_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        pay_date = (today + timedelta(days=51)).strftime('%Y-%m-%d')
        
        return DividendInfo(
            symbol=symbol,
            dividend_rate=data['rate'],
            dividend_yield=data['yield'],
            ex_date=ex_date,
            pay_date=pay_date,
            amount_per_share=data['amount']
        )
    
    def get_multiple_dividend_info(self, symbols: List[str]) -> List[DividendInfo]:
        """Get dividend information for multiple stocks"""
        return [self.get_dividend_info(symbol) for symbol in symbols]
    
    def get_high_yield_stocks(self, min_yield: float = 0.02) -> List[DividendInfo]:
        """Get stocks with dividend yield above minimum threshold"""
        dividend_data = self.get_multiple_dividend_info(self.dividend_stocks)
        return [d for d in dividend_data if d.dividend_yield >= min_yield]
    
    def to_json(self, symbols: List[str] = None) -> str:
        """Convert dividend data to JSON format for API consumption"""
        if symbols is None:
            symbols = self.dividend_stocks[:10]  # Limit to first 10 for performance
        
        dividend_data = self.get_multiple_dividend_info(symbols)
        return json.dumps([d.to_dict() for d in dividend_data], indent=2)

def main():
    """Main function for CLI usage and testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Dividend Tracker')
    parser.add_argument('symbols', nargs='*', default=['AAPL', 'MSFT', 'JNJ', 'PG', 'KO'], 
                        help='Stock symbols to track')
    parser.add_argument('--high-yield', type=float, metavar='MIN_YIELD',
                        help='Filter for high yield stocks with minimum yield')
    parser.add_argument('--json-only', action='store_true',
                        help='Output only JSON format')
    
    args = parser.parse_args()
    
    tracker = StockDividendTracker()
    
    if args.high_yield is not None:
        # Get high yield stocks
        dividend_data = tracker.get_high_yield_stocks(args.high_yield)
        symbols = [d.symbol for d in dividend_data]
    else:
        symbols = args.symbols
    
    if args.json_only:
        # Output only JSON for API consumption
        print(tracker.to_json(symbols))
    else:
        # Human-readable output
        print("Stock Dividend Tracker")
        print("=" * 50)
        
        for symbol in symbols:
            div_info = tracker.get_dividend_info(symbol)
            print(f"\n{symbol}:")
            print(f"  Dividend Rate: ${div_info.dividend_rate:.2f}")
            print(f"  Dividend Yield: {div_info.dividend_yield:.2%}")
            print(f"  Amount per Share: ${div_info.amount_per_share:.2f}")
            print(f"  Ex-Date: {div_info.ex_date or 'N/A'}")
            print(f"  Pay Date: {div_info.pay_date or 'N/A'}")
        
        # Also output JSON for integration testing
        print(f"\nJSON Output:")
        print(tracker.to_json(symbols))

if __name__ == "__main__":
    main()