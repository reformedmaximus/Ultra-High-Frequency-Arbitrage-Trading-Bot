from kucoin_websocket_handler import start_kucoin_websocket
from binance_websocket_handler import start_binance_websocket
from dotenv import load_dotenv
import os 
import asyncio
from kucoin_apis import KuCoinAPI
import logging

#INFO:root:Received message: {'id': 's13u6l50tc', 'type': 'welcome'} welcome message when websocket connection is successfull from kucoin
#INFO:root:Received message: {'id': '1717989479', 'type': 'ack'} ack message when topic subscription is successfull from kucoin



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
  kucoin_task = asyncio.create_task(start_kucoin_websocket(api))
  binance_task = asyncio.create_task(start_binance_websocket())
  
  # run both tasks concurrently 
  await asyncio.gather(kucoin_task, binance_task)


if __name__ == "__main__":
    asyncio.run(main())        