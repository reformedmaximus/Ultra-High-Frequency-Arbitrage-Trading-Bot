from websocket_handler import start_websocket
from dotenv import load_dotenv
import os 

load_dotenv() # take environment variables from .env
#hiding sensitive info for now in case I make this project public in the future 
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_passphrase = os.getenv('API_PASSPHRASE')

start_websocket(api_key, api_secret, api_passphrase)