#contains all interactions with kucoin apis
import time
import base64
import hmac
import hashlib
import json
import requests
import os 

class KuCoinAPI:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        self.api_passphrase = os.getenv('API_PASSPHRASE')
        self.base_url = 'https://api.kucoin.com'

    def sign(self, method, endpoint, body=None):
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method + endpoint
        if body:
            str_to_json = json.dumps(body)
            str_to_sign += str_to_json
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
        )
        passphrase = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), self.api_passphrase.encode('utf-8'), hashlib.sha256).digest()
        )
        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }
        return headers

    def get_24hr_stats(self, symbol):
        url = f'{self.base_url}/api/v1/market/stats?symbol={symbol}'
        headers = self.sign('GET', f'/api/v1/market/stats?symbol={symbol}')
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch data", "status_code": response.status_code, "message": response.text}

    def get_accounts(self):
        url = f'{self.base_url}/api/v1/accounts'
        headers = self.sign('GET', '/api/v1/accounts')
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    
    def get_websocket_token(self):
        url = f'{self.base_url}/api/v1/bullet-public'
        headers = self.sign('POST','/api/v1/bullet-public')
        response = requests.post(url, headers=headers)
        return response.json() if response.status_code == 200 else None 

# Usage
api_key = ""
api_secret = ""
api_passphrase = ""
api = KuCoinAPI(api_key, api_secret, api_passphrase)
#btc_stats = api.get_24hr_stats('BTC-USDT')
#print(btc_stats)

    
 