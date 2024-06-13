from kucoin_websocket_handler import start_kucoin_websocket
from binance_websocket_handler import start_binance_websocket
from dotenv import load_dotenv
import os 
import asyncio
from kucoin_apis import KuCoinAPI
import logging
import datetime

#INFO:root:Received message: {'id': 's13u6l50tc', 'type': 'welcome'} welcome message when websocket connection is successfull from kucoin
#INFO:root:Received message: {'id': '1717989479', 'type': 'ack'} ack message when topic subscription is successfull from kucoin

# global dictionary to hold the latest prices 
latest_prices = { 'kucoin': {"price": None, "time": None}, 'binance': {"price": None, "time": None} }

def update_price_and_compare_callback(exchange, price):
   #update global dictionary with latest price 
   latest_prices[exchange]= {"price":price , "time": datetime.datetime.now()} 
   binance = latest_prices['binance']
   kucoin = latest_prices['kucoin']
   if binance['price'] is not None and kucoin['price'] is not None:
      time_diff =abs((binance['time'] - kucoin['time']).total_seconds())
      price_diff = binance ['price']-kucoin['price']
      print(f"Binance: {binance['price']}, Kucoin: {kucoin['price']}, Time Diff : {time_diff}, Price Diff : {price_diff}")



load_dotenv() # take environment variables from .env
#hiding sensitive info for now in case I make this project public in the future 
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_passphrase = os.getenv('API_PASSPHRASE')

async def main():
  
  """  api = KuCoinAPI()
    while True:
        await start_kucoin_websocket(api)
        await asyncio.sleep(10) # wait before attempting to reconnect """
  api = KuCoinAPI()
  # start both websocket handlers 
  kucoin_task = asyncio.create_task(start_kucoin_websocket(api, lambda price: update_price_and_compare_callback('kucoin',price)))
  binance_task = asyncio.create_task(start_binance_websocket(lambda price: update_price_and_compare_callback('binance',price) ))
  
  # run both tasks concurrently 
  await asyncio.gather(kucoin_task, binance_task)


if __name__ == "__main__":
    asyncio.run(main())        