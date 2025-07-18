using Aspire.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

// Add the Stock API service
var stockApi = builder.AddProject<Projects.StockTickr_Api>("stockapi");

// Build and run the application
builder.Build().Run();
