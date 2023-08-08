import requests
import time
import csv
from tabulate import tabulate

# Telegram configurations
TELEGRAM_TOKEN = ""
CHAT_ID = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response.json()

def format_and_send(sorted_symbols):
    # Format the data for improved readability
    formatted_data = []
    for symbol, rate in sorted_symbols:
        # Format the rate to have 5 decimal places
        formatted_rate = f"{rate:.5f}"
        
        # Highlight rates that exceed certain thresholds
        if rate > 0.01:
            formatted_rate = f"<b>{formatted_rate}</b>"
        elif rate < -0.01:
            formatted_rate = f"<b>{formatted_rate}</b>"
        
        formatted_data.append([symbol, formatted_rate])

    # Create a message with the formatted data
    headers = ['Sym', 'Rate']
    message = tabulate(formatted_data, headers=headers, tablefmt='grid')

    # Send the message
    send_telegram_message(message)

def fetch_data():
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    headers = {
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-SIGN': '',
        'X-BAPI-API-KEY': '',
        'X-BAPI-TIMESTAMP': '',
        'X-BAPI-RECV-WINDOW': '{{recvWindow}}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    symbols_data = []
    for item in data['result']['list']:
        try:
            funding_rate = float(item['fundingRate'])
        except ValueError:
            funding_rate = 0.0
        symbols_data.append((item['symbol'], funding_rate))

    # Sort and pick top 10 symbols
    sorted_symbols = sorted(symbols_data, key=lambda x: abs(x[1]), reverse=True)[:10]


    with open('./sorted_symbols.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Symbol', 'FundingRate'])
        csvwriter.writerows(sorted_symbols)

    print(tabulate(sorted_symbols, headers=['Symbol', 'FundingRate']))

    # Check if any of the top 10 have a fundingRate > 0.01 or < -0.01
    trigger_push = any(rate > 0.01 or rate < -0.01 for _, rate in sorted_symbols)
    if trigger_push:
        format_and_send(sorted_symbols)

def periodic_fetch(interval):
    while True:
        fetch_data()
        time.sleep(interval)

# Fetch data every 60 seconds (you can adjust this value as needed)
periodic_fetch(3600)
