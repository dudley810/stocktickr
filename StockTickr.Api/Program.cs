using System.Diagnostics;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS for development
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowAll");

app.MapGet("/", () => "StockTickr Dividend Tracking API - Navigate to /swagger for API documentation");

// Health check endpoint
app.MapGet("/health", () => new { Status = "Healthy", Timestamp = DateTime.UtcNow });

// Helper method to execute Python scripts
async Task<string> ExecutePythonScript(string script, string arguments = "")
{
    try
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "python3",
            Arguments = $"{script} {arguments}",
            WorkingDirectory = "/home/runner/work/stocktickr/stocktickr/src",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = Process.Start(startInfo);
        if (process == null) throw new Exception("Failed to start Python process");

        var output = await process.StandardOutput.ReadToEndAsync();
        var error = await process.StandardError.ReadToEndAsync();
        
        await process.WaitForExitAsync();

        if (process.ExitCode != 0)
        {
            throw new Exception($"Python script failed: {error}");
        }

        return output;
    }
    catch (Exception ex)
    {
        throw new Exception($"Error executing Python script: {ex.Message}");
    }
}

// Get dividend information for a single stock
app.MapGet("/api/dividend/{symbol}", async (string symbol) =>
{
    try
    {
        var result = await ExecutePythonScript("dividend_tracker.py", $"--json-only {symbol.ToUpper()}");
        
        // Find the JSON part (starts with [ or {)
        var jsonStart = result.IndexOfAny(new char[] { '[', '{' });
        if (jsonStart == -1)
        {
            throw new Exception("No JSON output found from Python script");
        }
        
        var jsonPart = result.Substring(jsonStart).Trim();
        
        // Parse JSON output from Python script
        var jsonDoc = JsonDocument.Parse(jsonPart);
        var stockArray = jsonDoc.RootElement;
        
        if (stockArray.GetArrayLength() == 0)
        {
            return Results.NotFound(new { error = $"No data found for symbol {symbol}" });
        }
        
        var stockData = stockArray[0];
        
        return Results.Ok(new
        {
            symbol = stockData.GetProperty("symbol").GetString(),
            dividend_rate = stockData.GetProperty("dividend_rate").GetDouble(),
            dividend_yield = stockData.GetProperty("dividend_yield").GetDouble(),
            ex_date = stockData.GetProperty("ex_date").GetString(),
            pay_date = stockData.GetProperty("pay_date").GetString(),
            amount_per_share = stockData.GetProperty("amount_per_share").GetDouble(),
            last_updated = stockData.GetProperty("last_updated").GetString()
        });
    }
    catch (Exception ex)
    {
        return Results.BadRequest(new { error = ex.Message });
    }
})
.WithName("GetDividendInfo")
.WithOpenApi();

// Get dividend information for multiple stocks
app.MapPost("/api/dividends", async (List<string> symbols) =>
{
    try
    {
        var symbolsArg = string.Join(" ", symbols.Select(s => s.ToUpper()));
        var result = await ExecutePythonScript("dividend_tracker.py", $"--json-only {symbolsArg}");
        
        // Find the JSON part (starts with [ or {)
        var jsonStart = result.IndexOfAny(new char[] { '[', '{' });
        if (jsonStart == -1)
        {
            throw new Exception("No JSON output found from Python script");
        }
        
        var jsonPart = result.Substring(jsonStart).Trim();
        
        // Parse JSON output from Python script
        var jsonDoc = JsonDocument.Parse(jsonPart);
        var stockArray = jsonDoc.RootElement;
        var stocks = new List<object>();
        
        foreach (var stockData in stockArray.EnumerateArray())
        {
            stocks.Add(new
            {
                symbol = stockData.GetProperty("symbol").GetString(),
                dividend_rate = stockData.GetProperty("dividend_rate").GetDouble(),
                dividend_yield = stockData.GetProperty("dividend_yield").GetDouble(),
                ex_date = stockData.GetProperty("ex_date").GetString(),
                pay_date = stockData.GetProperty("pay_date").GetString(),
                amount_per_share = stockData.GetProperty("amount_per_share").GetDouble(),
                last_updated = stockData.GetProperty("last_updated").GetString()
            });
        }
        
        return Results.Ok(stocks);
    }
    catch (Exception ex)
    {
        return Results.BadRequest(new { error = ex.Message });
    }
})
.WithName("GetMultipleDividendInfo")
.WithOpenApi();

// Get high-yield dividend stocks
app.MapGet("/api/dividends/high-yield", async (double minYield = 0.02) =>
{
    try
    {
        var result = await ExecutePythonScript("dividend_tracker.py", $"--json-only --high-yield {minYield}");
        
        // Find the JSON part (starts with [ or {)
        var jsonStart = result.IndexOfAny(new char[] { '[', '{' });
        if (jsonStart == -1)
        {
            throw new Exception("No JSON output found from Python script");
        }
        
        var jsonPart = result.Substring(jsonStart).Trim();
        
        // Parse JSON output from Python script
        var jsonDoc = JsonDocument.Parse(jsonPart);
        var stockArray = jsonDoc.RootElement;
        var stocks = new List<object>();
        
        foreach (var stockData in stockArray.EnumerateArray())
        {
            if (stockData.GetProperty("dividend_yield").GetDouble() >= minYield)
            {
                stocks.Add(new
                {
                    symbol = stockData.GetProperty("symbol").GetString(),
                    dividend_rate = stockData.GetProperty("dividend_rate").GetDouble(),
                    dividend_yield = stockData.GetProperty("dividend_yield").GetDouble(),
                    ex_date = stockData.GetProperty("ex_date").GetString(),
                    pay_date = stockData.GetProperty("pay_date").GetString(),
                    amount_per_share = stockData.GetProperty("amount_per_share").GetDouble(),
                    last_updated = stockData.GetProperty("last_updated").GetString()
                });
            }
        }
        
        return Results.Ok(new
        {
            criteria = new { minimum_yield = minYield },
            count = stocks.Count,
            stocks = stocks
        });
    }
    catch (Exception ex)
    {
        return Results.BadRequest(new { error = ex.Message });
    }
})
.WithName("GetHighYieldStocks")
.WithOpenApi();

// Get default dividend portfolio
app.MapGet("/api/dividends/portfolio", async () =>
{
    try
    {
        var result = await ExecutePythonScript("dividend_tracker.py", "--json-only");
        
        // Find the JSON part (starts with [ or {)
        var jsonStart = result.IndexOfAny(new char[] { '[', '{' });
        if (jsonStart == -1)
        {
            throw new Exception("No JSON output found from Python script");
        }
        
        var jsonPart = result.Substring(jsonStart).Trim();
        return Results.Content(jsonPart, "application/json");
    }
    catch (Exception ex)
    {
        return Results.BadRequest(new { error = ex.Message });
    }
})
.WithName("GetDividendPortfolio")
.WithOpenApi();

app.Run();
