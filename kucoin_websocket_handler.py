from kucoin_apis import KuCoinAPI
import websockets
import json 
import time 
import threading
import logging 


logging.basicConfig(level=logging.INFO)

# function to start the WebSocket Connection 

async def start_kucoin_websocket(api):
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
                response = await ws.recv() #listening for incoming messages recv is receive 
                message = json.loads(response)
                #print("received message :", message).
                logging.info(f"********Received message from Kucoin********: {message}")
                await handle_ping(ws, message)
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

async def handle_ping(ws, message): 
    if message.get('type') == 'pong': 
        print("pong received")
    if time.time()-handle_ping.last_ping > 30: #send ping every 30 seconds 
        await ws.send(json.dumps({"id": str(int(time.time())), "type": "ping"})) 
        handle_ping.last_ping = time.time()

handle_ping.last_ping = time.time()

async def on_message (ws, message):
    data=json.loads(message)
    print("received message :",data)




    


