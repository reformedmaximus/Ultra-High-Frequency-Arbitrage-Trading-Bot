import asyncio 
import websockets
import json 
import datetime


async def start_binance_websocket(update_price_and_compare_callback):
    url="wss://stream.binance.com:9443/ws/btcusdt@trade"
    async with websockets.connect(url, ping_interval=None) as websocket: #disabled automatic ping management by websockets library 
        print("connected to binance websocket")
        while True:
            try:    
                message = await websocket.recv()
                data = json.loads(message) #convert json string into python data structure
                if 'p' in data: #check if price is in the message
                    price = float(data['p'])
                    update_price_and_compare_callback(price)
                    timestamp = datetime.datetime.now().isoformat()
                    log_message = f"{timestamp} Binance BTC/USDT price: {price} \n"
                    print(log_message)
                    with open("bitcoin_price_data_binance.txt","a") as file:
                         file.write(log_message)
                #responding to pings manually 
                if 'ping' in data:
                     await websocket.send(json.dumps({"pong": data['ping']}))
            except Exception as e:
                print(f"error occured : {e}")


"""if message is None:
                    #check if its a ping frame: 
                    await websocket.pong() # send a pong
                    print("pong sent in response to a ping in binance")
                else: 
                    #handle normal messages
                    response =json.loads(message) #convert json string into python data structure
                    print("********Received message from Binance********:", response)"""
                   
        
        