import asyncio 
import websockets
import json 


async def start_binance_websocket():
    url="wss://stream.binance.com:9443/ws/btcusdt@trade"
    async with websockets.connect(url) as websocket: 
        print("connected to binance websocket")
        while True: 
            response = await websocket.recv()
            message = json.loads(response)
            print("********Received message from Binance********:", message)