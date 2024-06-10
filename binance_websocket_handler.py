import asyncio 
import websockets
import json 


async def start_binance_websocket():
    url="wss://stream.binance.com:9443/ws/btcusdt@trade"
    async with websockets.connect(url, ping_interval=None) as websocket: #disabled automatic ping management by websockets library 
        print("connected to binance websocket")
        while True:
            try:
                message = await websocket.recv()
                if message is None:
                    #check if its a ping frame: 
                    await websocket.pong() # send a pong
                    print("pong sent in response to a ping in binance")
                else: 
                    #handle normal messages
                    response =json.loads(message) #convert json string into python data structure
                    print("********Received message from Binance********:", response)
            except websockets.ConnectionClosed as e:
                print(f"connection closed with error : {e}")
                break #reconnect         
        
        