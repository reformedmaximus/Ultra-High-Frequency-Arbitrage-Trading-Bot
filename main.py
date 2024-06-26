from kucoin_websocket_handler import start_kucoin_websocket
from binance_websocket_handler import start_binance_websocket
from dotenv import load_dotenv
import os 
import asyncio
from kucoin_apis import KuCoinAPI
import logging
import datetime
import psycopg2
from datetime import datetime, timezone


#INFO:root:Received message: {'id': 's13u6l50tc', 'type': 'welcome'} welcome message when websocket connection is successful from kucoin
#INFO:root:Received message: {'id': '1717989479', 'type': 'ack'} ack message when topic subscription is successful from kucoin

    
#database connection setup 
conn = psycopg2.connect("dbname=trading_data user=postgres password=mootaz2002")
cur = conn.cursor()

#function to insert data into database 
def insert_data(time, symbol,price_kucoin, price_binance):
    cur.execute(
        "INSERT INTO price_data (time, symbol, price_kucoin,price_binance) VALUES (%s,%s,%s,%s)",
        (time,symbol,price_kucoin,price_binance)
    )
    conn.commit()
    


# global dictionary to hold the latest prices 
latest_prices = { 'kucoin': {"price": None, "time": None}, 'binance': {"price": None, "time": None} }
binance_snapshot = {"price": None, "time": None}

def update_price_and_compare_callback(exchange, price):
   
    current_time = datetime.now(timezone.utc)

    #normal data tracking and price difference starts from here 
    # Update the latest prices and timestamp
    latest_prices[exchange] = {"price": price, "time": current_time}
    # retrieve the latest prices
    binance = latest_prices['binance']
    kucoin = latest_prices['kucoin']
    

    # set a binance snapshot in order to compare kucoin's current & real time updated price to it 
    if exchange == 'binance':
        binance_snapshot['price'] = price
        binance_snapshot['time'] = current_time
        
    elif exchange =='kucoin' and binance_snapshot['price'] is not None: # checking only when binance has a valid snapshot
        price_data= f"Snapshot set at Binance with price {binance_snapshot['price']}, Kucoin price at snapshot with price {price} \n"
        with open("price_data.txt", "a") as file:
            file.write(price_data)
        #price_tolerance = 0.1       
        #if abs(price - binance_snapshot['price']) <= price_tolerance:
        if price >= binance_snapshot['price']:
            time_diff = ( current_time - binance_snapshot['time']).total_seconds()
            arbitrage_log = f"time duration that took Kucoin to catchup to Binance is {time_diff} seconds \n"
            print(arbitrage_log)
            with open("arbitrageLog.txt", "a") as file:
             file.write(arbitrage_log) 
             
                 # update the Binance snapshot to the latest price and time so we can continue the cycle of tracking
             binance_snapshot['price']=binance['price']
             binance_snapshot['time']=binance['time']
     
             
    #checking if both exchanges sent prices and inserting in the database
    if latest_prices['kucoin']['price'] is not None and latest_prices['binance']['price'] is not None:
        insert_data(current_time,"BTC-USDT",latest_prices['kucoin']['price'],latest_prices['binance']['price'])         
         
    """ # get the current kucoin price at the time we took the binance snapshot 
        kucoin_price_at_snapshot=latest_prices['kucoin']['price']
        if kucoin_price_at_snapshot is not None:
            price_diff_at_snapshot= price - kucoin_price_at_snapshot #price is the binance snapshot price
            price_data= f"Snapshot set at Binance with price {price}, Kucoin price at snapshot with price {kucoin_price_at_snapshot}, Price Difference : {price_diff_at_snapshot} \n"
            with open("price_data.txt", "a") as file:
             file.write(price_data)"""

     #kucoin or binance['price'] is the current updated price
     #check kucoin's price against the binance snapshot 
"""  if kucoin['price'] is not None and binance_snapshot['price'] is not None:
     if kucoin['price'] >= binance_snapshot['price']:
           time_diff = ( current_time - binance_snapshot['time']).total_seconds()
           arbitrage_log = f"time duration that took Kucoin to catchup to Binance is {time_diff} \n"
           print(arbitrage_log)
           with open("arbitrageLog.txt", "a") as file:
            file.write(arbitrage_log)"""

        

      


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

    
""""
def update_price_and_compare_callback(exchange, price):
   global last_binance_price, last_binance_time 
    

   #update global dictionary with latest price 
   latest_prices[exchange]= {"price":price , "time": datetime.datetime.now()} 
   binance = latest_prices['binance']
   kucoin = latest_prices['kucoin']

   if exchange =='binance':
        #update last_binance price and last_binance_time if binance price changes 
        if last_binance_price != binance['price']:
             last_binance_price = binance['price']
             last_binance_time = binance['time']


   if binance['price'] is not None and kucoin['price'] is not None:
      if kucoin['price']>=last_binance_price: 
         time_diff = (kucoin['time'] - last_binance_time).total_seconds()
         price_diff = kucoin ['price']-binance['price']
         arbitrage_log = f"kucoin: {kucoin['price']}, binance: {binance['price']}, Time Diff : {time_diff}, Price Diff : {price_diff} / Kucoin's btc price is higher than Binance's last current price \n"
         with open("arbitrageLog.txt","a") as file:
                     file.write(arbitrage_log) 
      elif  kucoin['price']<=last_binance_price:    
            time_diff = (last_binance_time - kucoin['time']).total_seconds()
            price_diff = binance ['price'] - kucoin['price']
            arbitrage_log = f"binance: {binance['price']}, kucoin: {kucoin['price']}, Time Diff : {time_diff}, Price Diff : {price_diff} / Binance last current btc price is higher than Kucoin's price \n"
            with open("arbitrageLog.txt","a") as file:
                     file.write(arbitrage_log)  
          """