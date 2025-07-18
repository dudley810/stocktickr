# StockTickr

A .NET Aspire microservice application for tracking stock dividend information with Python integration.

## Overview

StockTickr is a comprehensive dividend tracking system that combines:
- Python-based dividend data collection using Yahoo Finance
- .NET Aspire microservice architecture
- RESTful API for dividend information
- Real-time stock dividend tracking with ex-dates, pay dates, yields, and amounts

## Features

### 🔹 Dividend Tracking
- **Ex-Date**: When you must own the stock to receive the dividend
- **Pay Date**: When the dividend payment is made
- **Dividend Yield**: Annual dividend percentage
- **Amount per Share**: Dividend payment per share
- **High-yield filtering**: Find stocks with yields above specified thresholds

### 🔹 API Endpoints
- `GET /api/dividend/{symbol}` - Get dividend info for a single stock
- `POST /api/dividends` - Get dividend info for multiple stocks  
- `GET /api/dividends/high-yield?minYield=0.02` - Filter high-yield dividend stocks
- `GET /api/dividends/portfolio` - Get default dividend-focused portfolio
- `GET /health` - Health check endpoint
- `GET /swagger` - API documentation

### 🔹 Technology Stack
- **.NET 8** - Web API and Aspire orchestration
- **Python 3.12** - Dividend data collection with yfinance
- **Aspire Hosting** - Distributed application orchestration
- **Swagger/OpenAPI** - API documentation
- **Yahoo Finance** - Real-time stock data source

## Project Structure

```
├── src/
│   ├── stocktickr.py          # Original GUI stock ticker
│   ├── dividend_tracker.py    # Enhanced dividend tracking module
│   └── simple_test.py         # Integration test helpers
├── StockTickr.Api/            # ASP.NET Core Web API
│   ├── Program.cs             # API endpoints and Python integration
│   └── *.csproj               # Project configuration
├── StockTickr.AppHost/        # .NET Aspire orchestration
│   ├── Program.cs             # Aspire hosting configuration
│   └── *.csproj               # Aspire project configuration
├── StockTickr.Aspire.sln      # Solution file
└── requirements.txt           # Python dependencies
```

## Quick Start

### Prerequisites
- .NET 8 SDK
- Python 3.12+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dudley810/stocktickr.git
   cd stocktickr
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the .NET solution**
   ```bash
   dotnet build StockTickr.Aspire.sln
   ```

### Running the Application

#### Option 1: Run API directly
```bash
cd StockTickr.Api
dotnet run
```
Navigate to: http://localhost:5297/swagger

#### Option 2: Run with Aspire orchestration
```bash
cd StockTickr.AppHost
dotnet run
```

## API Examples

### Get single stock dividend info
```bash
curl http://localhost:5297/api/dividend/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "dividend_rate": 0.96,
  "dividend_yield": 0.0044,
  "ex_date": "2025-08-17",
  "pay_date": "2025-09-07",
  "amount_per_share": 0.24,
  "last_updated": "2025-07-18T13:16:10.118953"
}
```

### Get multiple stocks
```bash
curl -X POST http://localhost:5297/api/dividends \
  -H "Content-Type: application/json" \
  -d '["AAPL", "MSFT", "JNJ"]'
```

### Get high-yield dividend stocks
```bash
curl "http://localhost:5297/api/dividends/high-yield?minYield=0.02"
```

**Response:**
```json
{
  "criteria": { "minimum_yield": 0.02 },
  "count": 3,
  "stocks": [
    {
      "symbol": "JNJ",
      "dividend_rate": 4.76,
      "dividend_yield": 0.0301,
      "ex_date": "2025-08-17",
      "pay_date": "2025-09-07",
      "amount_per_share": 1.19,
      "last_updated": "2025-07-18T13:16:20.365493"
    }
  ]
}
```

## Investment Strategy

StockTickr focuses on **dividend growth investing** strategies:

- **High-quality dividend payers**: Companies with consistent dividend payments
- **Dividend aristocrats**: S&P 500 companies with 25+ years of dividend increases
- **Yield analysis**: Compare dividend yields across sectors
- **Ex-date tracking**: Optimize purchase timing for dividend capture

**Default Portfolio** includes dividend-focused stocks:
- Technology: AAPL, MSFT, INTC, IBM
- Healthcare: JNJ
- Consumer Goods: PG, KO, PEP, MCD
- Financials: JPM, BAC
- Energy: XOM, CVX
- Industrials: MMM, CAT, HD
- Telecom: VZ, T
- Tobacco: MO

## Development

### Python Module (dividend_tracker.py)
```python
from src.dividend_tracker import StockDividendTracker

tracker = StockDividendTracker()
div_info = tracker.get_dividend_info("AAPL")
print(f"Dividend yield: {div_info.dividend_yield:.2%}")
```

### .NET Integration
The API uses subprocess calls to execute Python scripts, providing reliable integration between .NET and Python without complex interop dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Deployment

### Docker Support (Future)
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0
# Python runtime installation
# Application deployment
```

### Azure Container Apps
The application is designed for cloud deployment using:
- Azure Container Apps for Aspire hosting
- Application Insights for monitoring
- Azure Key Vault for API keys

## License

This project is open source. See LICENSE file for details.

## Disclaimer

**This software is for educational and informational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions. Stock prices and dividend information may be delayed or inaccurate.**