import pygame
import yfinance as yf
import time

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((900, 200))
pygame.display.set_caption('Stock Ticker')
font = pygame.font.SysFont("Courier", 36)
clock = pygame.time.Clock()

# Define stock symbols
symbols = ['AAPL','AMZN','AVGO', 'ADC','MO','JPM','TSLA', 'GOOGL', 'MSFT','NVDA','TSM']

def get_prices(symbols):
    prices = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[-1]
            prices.append(f"{symbol}:${price:.2f}")
        except Exception as e:
            prices.append(f"{symbol}:N/A")
    return ', '.join(prices)

# Initial text
text = get_prices(symbols)
x = screen.get_width()

running = True
update_interval = 60  # seconds
last_update = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update prices at specified intervals
    if time.time() - last_update > update_interval:
        text = get_prices(symbols)
        x = screen.get_width()
        last_update = time.time()

    screen.fill((0, 0, 0))
    rendered = font.render(text, True, (0, 255, 0))
    screen.blit(rendered, (x, 30))
    pygame.display.flip()
    x -= 2
    if x < -rendered.get_width():
        x = screen.get_width()
    clock.tick(30)

pygame.quit()
