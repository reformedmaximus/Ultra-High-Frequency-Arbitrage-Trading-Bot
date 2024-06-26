from kucoin_apis import KuCoinAPI
import websockets
import json 
import time 
import threading
import logging 
import datetime


logging.basicConfig(level=logging.INFO)

# function to start the WebSocket Connection 

async def start_kucoin_websocket(api,update_price_and_compare_callback):
    logging.info("Requesting WebSocket token...")
    websocket_token = api.get_websocket_token()
    kucoin_ws_url = websocket_token['data']['instanceServers'][0]['endpoint'] + "?token=" + websocket_token['data']['token'] #this extracts the websocket endpoint wss://ws-api-spot.kucoin.com/ from the response you get when you request a websocket token + we add our own token ( cuz of dynamic endpoint )
    logging.info(f"Connecting to WebSocket at {kucoin_ws_url}...")
    async with websockets.connect(kucoin_ws_url) as ws:
        #await subscribe(ws,"/market/candles:BTC-USDT_1hour")
        logging.info(f"Connecting to WebSocket at {kucoin_ws_url}...")
        await subscribe(ws,"/market/ticker:BTC-USDT")

        while True: 
            try:
                message = await ws.recv() #listening for incoming messages recv is receive 
                data = json.loads(message) #convert json string into nested python dictionnary ( collection of key-value pairs )
                
                if 'type' in data and data['type'] in ['pong','ack','welcome']:
                    logging.info(f"Received {data['type']} message: {data}")
                    continue
                
                if 'data' in data and 'price' in data['data']:
                   price = float(data['data']['price'])
                   update_price_and_compare_callback(price) # call the callback with the new price  
                else:
                    logging.error(f"unexpected message structure : {data}")
                       
                  # Send ping to keep connection alive if needed
                await handle_ping(ws,data)
                
                     
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed, attempting to reconnect...")    
                break #exit loop to reconnect outside this block 
            except Exception as e:
                logging.error(f"An error occurred: {e}")


async def subscribe(ws, topic):
    message= json.dumps({
        "id": str(int(time.time())),
        "type": "subscribe",
        "topic": topic,
        "response": True
    })
    await ws.send(message)
    print(f"subscribed to {topic}")


"""async def handle_ping(ws, message):
    if isinstance(message, dict):
        if 'type' in message and message['type'] == 'pong':
            print("pong received")
        if time.time() - handle_ping.last_ping > 30:  # send ping every 30 seconds
            await ws.send(json.dumps({"id": str(int(time.time())), "type": "ping"}))
            handle_ping.last_ping = time.time()"""

async def handle_ping(ws, data): 
    if data.get('type') == 'pong': 
        print("pong received")
    if time.time()-handle_ping.last_ping > 30: #send ping every 30 seconds 
        await ws.send(json.dumps({"id": str(int(time.time())), "type": "ping"})) 
        handle_ping.last_ping = time.time()     
handle_ping.last_ping = time.time()

""" latest handle ping function i tried 
async def handle_ping(ws):
    handle_ping.last_ping = time.time()  # Initialize last ping time    
    if time.time() - handle_ping.last_ping > 30:  # Send ping every 30 seconds
        await ws.send(json.dumps({"id": str(int(time.time())), "type": "ping"}))
        handle_ping.last_ping = time.time()
        print("Ping sent")
"""

async def on_message (ws, message):
    data=json.loads(message)
    print("received message :",data)




    


