from kucoin_apis import KuCoinAPI
import websocket 
import json 
import time 
import threading


def send_ping(ws):
    ping_message = json.dumps({"id": str(int(time.time())), "type":"ping"})
    while True:
        time.sleep(18) #ping interval per kucoin's conditions 
        try: 
            if ws.keep_running:
                ws.send(ping_message)  #send a websocket formatted ping message not just a normal message 
            else: 
                break #break loop if websocket is no longer running 
        except Exception as e: 
            print(f"error sending ping:{e}")
            break


def on_message(ws, message):
    print("received message:")
    print(message)

def on_error(ws, error):
    print("error:", error)


def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed with status {close_status_code}: {close_msg}")

def on_open(ws):
    def run(*args):
        subscription_message = json.dumps({
            "id": str(int(time.time())),
            "type": "subscribe",
            "topic": "/market/candles:BTC-USDT_1hour",
            "privateChannel": False,
            "response": True
        })    
        ws.send(subscription_message)
        print("websocket opened and subscription message sent")
        ws.send(json.dumps({
            "id": str(int(time.time())),
            "type": "subscribe",
            "topic": "/market/ticker:BTC-USDT",
            "response": True
        }))

    threading.Thread(target=run).start()

# function to start the WebSocket Connection 

def start_websocket(api_key, api_secret, api_passphrase):
    api = KuCoinAPI(api_key, api_secret, api_passphrase)
    websocket_token = api.get_websocket_token()
    if websocket_token and 'token' in websocket_token['data']:
        ws_url = websocket_token['data']['instanceServers'][0]['endpoint'] + "?token=" + websocket_token['data']['token'] #this extracts the websocket endpoint wss://ws-api-spot.kucoin.com/ from the response you get when you request a websocket token + we add our own token ( cuz of dynamic endpoint )
        ws = websocket.WebSocketApp(ws_url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()
    else:
        print("failed to get websocket token")


