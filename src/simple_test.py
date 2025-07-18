#!/usr/bin/env python3

def simple_test():
    """Simple test function for C# integration"""
    return {
        "message": "Hello from Python!",
        "test_stock": {
            "symbol": "AAPL",
            "dividend_rate": 0.96,
            "dividend_yield": 0.0044,
            "ex_date": "2025-08-17",
            "pay_date": "2025-09-07",
            "amount_per_share": 0.24
        }
    }

if __name__ == "__main__":
    result = simple_test()
    print(result)